# MicroDoser Documentation

Complete documentation for the Dose Every Well precision dosing system.

---

## 📚 Documentation Files

| Document | Description |
|----------|-------------|
| **[quick-start.md](quick-start.md)** | Installation, setup, basic usage, and troubleshooting |
| **[python-api.md](python-api.md)** | Complete Python API reference |
| **[web-api.md](web-api.md)** | Web service setup and REST API reference |
| **[architecture.md](architecture.md)** | System design and configuration guide |
| **[examples.md](examples.md)** | Detailed workflow examples |

---

## 🚀 Quick Links

### For New Users
1. Start with [Quick Start](quick-start.md)
2. Run example scripts from `../examples/`
3. Read [Python API](python-api.md) for details

### For Configuration
- [Architecture & Configuration](architecture.md) - Hardware setup and YAML configs
- [Quick Start](quick-start.md#hardware-setup) - Hardware troubleshooting

### For Developers
- [Architecture](architecture.md#design-philosophy) - System design
- [Python API](python-api.md) - Implementation details
- [Web API](web-api.md) - REST API and web service
- [Examples](examples.md) - Usage patterns

---

## 📖 Documentation by Task

### Installation & Setup
- [Installation](quick-start.md#installation)
- [Hardware Setup](quick-start.md#hardware-setup)
- [First-Time Calibration](quick-start.md#first-time-calibration)

### Basic Usage
- [Standalone Weighing](quick-start.md#1-standalone-weighing-station)
- [Automated Dosing](quick-start.md#2-with-cnc-automated-dosing)
- [Batch Processing](quick-start.md#3-batch-dosing)

### Configuration
- [Plate Types](architecture.md#custom-plate-types)
- [CNC Settings](architecture.md#cnc-configuration)
- [Flow Rate Calibration](architecture.md#flow-rate-calibration)

### API Reference
- [MicroDoser Class](python-api.md#micodoser)
- [CNCDosingSystem Class](python-api.md#cncdosingsystem)
- [REST API Endpoints](web-api.md#api-endpoints)
- [All Methods](python-api.md#api-reference)

### Troubleshooting
- [Common Issues](quick-start.md#troubleshooting)
- [Configuration Problems](architecture.md#troubleshooting-configuration)

---

## 🎯 Learning Path

### Beginner
1. Read [Quick Start](quick-start.md)
2. Run `examples/example_standalone.py`
3. Understand basic API

### Intermediate
1. Run `examples/example_with_cnc.py`
2. Calibrate your system
3. Read [Architecture & Configuration](architecture.md)
4. Create custom workflows

### Advanced
1. Study [System Design](architecture.md#design-philosophy)
2. Read complete [Python API](python-api.md)
3. Integrate with external systems
4. Contribute to the project

---

## 🔗 External Resources

### Hardware
- [Sartorius Balance Documentation](https://www.sartorius.com/)
- [PCA9685 Datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)

### Software
- [Python Documentation](https://docs.python.org/3/)
- [GRBL Wiki](https://github.com/gnea/grbl/wiki)
- [Opentrons API](https://docs.opentrons.com/) (future integration)

---

## 📧 Support

- **Documentation Issues**: Open an issue on GitHub
- **Usage Questions**: Check [Examples](examples.md) or [Python API](python-api.md)
- **Email**: yangcyril.cao@utoronto.ca

---

## 🤝 Contributing to Documentation

Documentation contributions are welcome!

**To add/update documentation:**

1. Edit the relevant `.md` file
2. Follow existing formatting
3. Test code examples
4. Update this index if adding new docs
5. Submit a pull request

**Documentation Style Guide:**

- Use clear, concise language
- Include code examples for all features
- Add troubleshooting sections
- Keep examples up-to-date
- Use consistent formatting
- No all-caps filenames

---

**Last Updated**: January 2025  
**Package Version**: 0.7.0
