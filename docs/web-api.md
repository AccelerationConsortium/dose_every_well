# Web API Service

Complete guide to deploying MicroDoser as a web service with REST API for remote control.

---

## Table of Contents

- [Overview](#overview)
- [Installation with uv](#installation-with-uv)
- [Service Setup](#service-setup)
- [API Endpoints](#api-endpoints)
- [Client Usage](#client-usage)
- [Troubleshooting](#troubleshooting)

---

## Overview

### Architecture

```
┌─────────────────┐         HTTP/REST          ┌──────────────────┐
│  Client         │ ◄────────────────────────► │  Raspberry Pi 5  │
│  (Any device)   │         (WiFi/LAN)         │  + MicroDoser    │
│                 │                             │  + FastAPI       │
└─────────────────┘                             └──────────────────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │   Hardware   │
                                                  │  - Balance   │
                                                  │  - Loader    │
                                                  │  - CNC       │
                                                  └──────────────┘
```

### Features

- ✅ Remote control via HTTP REST API
- ✅ Auto-start on boot
- ✅ Persistent service (survives SSH disconnection)
- ✅ Real-time status updates
- ✅ Error handling and feedback
- ✅ Authentication support
- ✅ WebSocket for real-time monitoring (optional)

---

## Installation with uv

### Step 1: Install uv

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Install uv (fast Python package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
uv --version
```

### Step 2: Clone Repository and Setup Environment

```bash
# Clone repository
cd ~
git clone https://github.com/AccelerationConsortium/dose_every_well.git
cd dose_every_well

# Create virtual environment with uv
uv venv

# Activate environment
source .venv/bin/activate

# Install package with uv (much faster than pip)
uv pip install -e .

# Install web service dependencies
uv pip install fastapi uvicorn python-multipart websockets
```

### Step 3: Verify Installation

```bash
# Test imports
python -c "from dose_every_well import MicroDoser; print('✓ MicroDoser installed')"
python -c "from fastapi import FastAPI; print('✓ FastAPI installed')"
```

---

## Service Setup

### Step 1: Create API Server

Create the API server file:

```bash
nano ~/dose_every_well/api_server.py
```

Paste the following content:

```python
#!/usr/bin/env python3
"""
MicroDoser Web API Service
FastAPI-based REST API for remote control of MicroDoser system.
"""

import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dose_every_well import MicroDoser, CNCDosingSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/dose_every_well/api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state
doser: Optional[MicroDoser] = None
dosing_system: Optional[CNCDosingSystem] = None
system_status = {
    "initialized": False,
    "plate_loaded": False,
    "busy": False,
    "error": None
}

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MicroDoser API service...")
    try:
        await initialize_system()
        logger.info("MicroDoser API service ready")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MicroDoser API service...")
    await shutdown_system()
    logger.info("MicroDoser API service stopped")

# Create FastAPI app
app = FastAPI(
    title="MicroDoser API",
    description="REST API for MicroDoser precision dosing system",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class DoseRequest(BaseModel):
    well: str
    target_mg: float
    verify: bool = True

class DosePlateRequest(BaseModel):
    well_targets: Dict[str, float]
    verify: bool = True

class SystemConfig(BaseModel):
    balance_port: str = "/dev/ttyUSB1"
    plate_type: str = "shallow_plate"
    cnc_port: Optional[str] = None

# Helper functions
async def initialize_system():
    """Initialize MicroDoser system."""
    global doser, dosing_system, system_status
    
    try:
        # Initialize CNC dosing system (optional)
        try:
            dosing_system = CNCDosingSystem(cnc_port='/dev/ttyUSB0')
            dosing_system.initialize()
            logger.info("CNC dosing system initialized")
        except Exception as e:
            logger.warning(f"CNC not available: {e}")
            dosing_system = None
        
        # Initialize MicroDoser
        doser = MicroDoser(
            balance_port='/dev/ttyUSB1',
            plate_type='shallow_plate',
            dosing_system=dosing_system
        )
        
        system_status["initialized"] = True
        system_status["error"] = None
        logger.info("MicroDoser initialized successfully")
        
    except Exception as e:
        system_status["error"] = str(e)
        logger.error(f"Initialization failed: {e}")
        raise

async def shutdown_system():
    """Shutdown MicroDoser system."""
    global doser, dosing_system
    
    if doser:
        try:
            doser.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    doser = None
    dosing_system = None
    system_status["initialized"] = False

def check_system():
    """Check if system is initialized."""
    if not system_status["initialized"] or doser is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    if system_status["busy"]:
        raise HTTPException(status_code=409, detail="System busy")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "MicroDoser API",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/api/status")
async def get_status():
    """Get system status."""
    try:
        if doser:
            doser_status = doser.get_status()
            system_status.update(doser_status)
        
        return {
            "status": "success",
            "system_status": system_status
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/api/initialize")
async def initialize(config: SystemConfig):
    """Initialize or reinitialize system with config."""
    try:
        await shutdown_system()
        await initialize_system()
        return {"status": "success", "message": "System initialized"}
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plate/load")
async def load_plate():
    """Load plate onto balance."""
    check_system()
    
    try:
        system_status["busy"] = True
        doser.load_plate()
        system_status["plate_loaded"] = True
        system_status["busy"] = False
        
        return {"status": "success", "message": "Plate loaded"}
    except Exception as e:
        system_status["busy"] = False
        logger.error(f"Error loading plate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plate/unload")
async def unload_plate():
    """Unload plate from balance."""
    check_system()
    
    try:
        system_status["busy"] = True
        doser.unload_plate()
        system_status["plate_loaded"] = False
        system_status["busy"] = False
        
        return {"status": "success", "message": "Plate unloaded"}
    except Exception as e:
        system_status["busy"] = False
        logger.error(f"Error unloading plate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/balance/read")
async def read_balance():
    """Read current balance value."""
    check_system()
    
    try:
        mass_g = doser.read_balance()
        mass_mg = mass_g * 1000
        
        return {
            "status": "success",
            "mass_g": mass_g,
            "mass_mg": mass_mg
        }
    except Exception as e:
        logger.error(f"Error reading balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/balance/tare")
async def tare_balance():
    """Tare the balance."""
    check_system()
    
    try:
        doser.tare_balance()
        return {"status": "success", "message": "Balance tared"}
    except Exception as e:
        logger.error(f"Error taring balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dose/well")
async def dose_well(request: DoseRequest):
    """Dose material to a single well."""
    check_system()
    
    if not dosing_system:
        raise HTTPException(status_code=503, detail="Dosing system not available")
    
    try:
        system_status["busy"] = True
        
        result = doser.dose_to_well(
            well=request.well,
            target_mg=request.target_mg,
            verify=request.verify
        )
        
        system_status["busy"] = False
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        system_status["busy"] = False
        logger.error(f"Error dosing well {request.well}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dose/plate")
async def dose_plate(request: DosePlateRequest, background_tasks: BackgroundTasks):
    """Dose material to multiple wells."""
    check_system()
    
    if not dosing_system:
        raise HTTPException(status_code=503, detail="Dosing system not available")
    
    try:
        system_status["busy"] = True
        
        results = doser.dose_plate(
            well_targets=request.well_targets,
            verify=request.verify
        )
        
        system_status["busy"] = False
        
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        system_status["busy"] = False
        logger.error(f"Error dosing plate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/shutdown")
async def shutdown():
    """Shutdown the system gracefully."""
    try:
        await shutdown_system()
        return {"status": "success", "message": "System shutdown"}
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Make it executable:

```bash
chmod +x ~/dose_every_well/api_server.py
```

### Step 2: Create systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/microdose-api.service
```

Paste the following:

```ini
[Unit]
Description=MicroDoser API Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/dose_every_well
Environment="PATH=/home/pi/dose_every_well/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/pi/dose_every_well/.venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/home/pi/dose_every_well/service.log
StandardError=append:/home/pi/dose_every_well/service_error.log

[Install]
WantedBy=multi-user.target
```

### Step 3: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable microdose-api.service

# Start service now
sudo systemctl start microdose-api.service

# Check status
sudo systemctl status microdose-api.service

# View logs
sudo journalctl -u microdose-api.service -f
```

### Step 4: Test API

```bash
# Test from Raspberry Pi
curl http://localhost:8000/

# Test from another device on network
curl http://raspberrypi.local:8000/api/status
```

---

## API Endpoints

### System Status

**GET** `/api/status`

Get current system status.

**Response:**
```json
{
  "status": "success",
  "system_status": {
    "initialized": true,
    "plate_loaded": false,
    "busy": false,
    "error": null
  }
}
```

### Plate Operations

**POST** `/api/plate/load`

Load plate onto balance.

**Response:**
```json
{
  "status": "success",
  "message": "Plate loaded"
}
```

**POST** `/api/plate/unload`

Unload plate from balance.

### Balance Operations

**GET** `/api/balance/read`

Read current balance value.

**Response:**
```json
{
  "status": "success",
  "mass_g": 0.0052,
  "mass_mg": 5.2
}
```

**POST** `/api/balance/tare`

Tare the balance to zero.

### Dosing Operations

**POST** `/api/dose/well`

Dose material to a single well.

**Request:**
```json
{
  "well": "A1",
  "target_mg": 5.0,
  "verify": true
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "well": "A1",
    "target_mg": 5.0,
    "actual_mg": 5.2,
    "error_mg": 0.2
  }
}
```

**POST** `/api/dose/plate`

Dose material to multiple wells.

**Request:**
```json
{
  "well_targets": {
    "A1": 5.0,
    "A2": 3.0,
    "B1": 7.0
  },
  "verify": true
}
```

---

## Client Usage

### Python Client

```python
import requests

# Base URL
BASE_URL = "http://raspberrypi.local:8000"

# Check status
response = requests.get(f"{BASE_URL}/api/status")
print(response.json())

# Load plate
response = requests.post(f"{BASE_URL}/api/plate/load")
print(response.json())

# Dose single well
response = requests.post(
    f"{BASE_URL}/api/dose/well",
    json={"well": "A1", "target_mg": 5.0, "verify": True}
)
result = response.json()
print(f"Dosed {result['result']['actual_mg']:.2f} mg to A1")

# Unload plate
response = requests.post(f"{BASE_URL}/api/plate/unload")
print(response.json())
```

### JavaScript Client

```javascript
const BASE_URL = 'http://raspberrypi.local:8000';

// Check status
fetch(`${BASE_URL}/api/status`)
  .then(response => response.json())
  .then(data => console.log(data));

// Dose well
fetch(`${BASE_URL}/api/dose/well`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    well: 'A1',
    target_mg: 5.0,
    verify: true
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### curl Examples

```bash
# Get status
curl http://raspberrypi.local:8000/api/status

# Load plate
curl -X POST http://raspberrypi.local:8000/api/plate/load

# Read balance
curl http://raspberrypi.local:8000/api/balance/read

# Dose well
curl -X POST http://raspberrypi.local:8000/api/dose/well \
  -H "Content-Type: application/json" \
  -d '{"well": "A1", "target_mg": 5.0, "verify": true}'

# Dose multiple wells
curl -X POST http://raspberrypi.local:8000/api/dose/plate \
  -H "Content-Type: application/json" \
  -d '{"well_targets": {"A1": 5.0, "A2": 3.0}, "verify": true}'
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status microdose-api.service

# View detailed logs
sudo journalctl -u microdose-api.service -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Test manually
cd ~/dose_every_well
source .venv/bin/activate
python api_server.py
```

### Cannot Connect from Client

```bash
# Check if service is running
sudo systemctl status microdose-api.service

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp

# Test locally first
curl http://localhost:8000/api/status

# Find Raspberry Pi IP
hostname -I
```

### Hardware Errors

```bash
# Check hardware connections
i2cdetect -y 1  # Should show 0x40
ls /dev/ttyUSB*  # Should show balance and CNC

# Check permissions
groups  # Should include dialout, gpio, i2c

# View application logs
tail -f ~/dose_every_well/api_server.log
```

### Service Management

```bash
# Stop service
sudo systemctl stop microdose-api.service

# Restart service
sudo systemctl restart microdose-api.service

# Disable auto-start
sudo systemctl disable microdose-api.service

# View real-time logs
sudo journalctl -u microdose-api.service -f
```

---

## Security Considerations

### Add Authentication

Install dependencies:

```bash
uv pip install python-jose passlib python-multipart
```

Add to `api_server.py`:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Implement token verification
    if credentials.credentials != "your-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials.credentials

# Protect endpoints
@app.post("/api/dose/well")
async def dose_well(request: DoseRequest, token: str = Depends(verify_token)):
    # ... endpoint code
```

### Use HTTPS

```bash
# Install certbot
sudo apt install certbot

# Generate certificate (requires domain name)
sudo certbot certonly --standalone -d yourdomain.com

# Update service to use HTTPS
# Modify uvicorn command in service file:
# --ssl-keyfile /etc/letsencrypt/live/yourdomain.com/privkey.pem
# --ssl-certfile /etc/letsencrypt/live/yourdomain.com/fullchain.pem
```

---

## Next Steps

- Add WebSocket support for real-time updates
- Implement job queue for long-running operations
- Add database logging of all operations
- Create web dashboard UI
- Implement user authentication and authorization
- Add API rate limiting

---

## See Also

- [Quick Start](quick-start.md) - Basic installation
- [Python API](python-api.md) - Python API reference
- [Architecture](architecture.md) - System design

