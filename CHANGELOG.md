# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-16

### Added
- Initial release of NLP2CMD framework
- Core converter architecture with BaseConverter
- ModelWrapper for LLM integration (supports models up to 3B parameters)
- Text2Env converter for .env file management
  - Natural language commands for setting, adding, deleting variables
  - Backup support
  - Validation and safety checks
- Text2Bash converter for bash script generation
  - Common command patterns
  - LLM-based generation for complex commands
  - Security validation
  - Dry run mode
- Text2Makefile converter for Make automation
  - Target parsing and execution
  - Parameter support
  - Makefile analysis
- Text2Docker converter for container management
  - Common service configurations (Postgres, Redis, MySQL, etc.)
  - Container lifecycle management
  - Port and volume mapping
- Pipeline system for combining multiple converters
  - Sequential execution
  - Error handling and rollback
  - Execution history and statistics
- Security features
  - Safe mode with dangerous pattern detection
  - Command validation
  - Input sanitization
  - Whitelist support
- Utility modules
  - Parsers for .env, Makefile, Dockerfile, and config files
  - Validators for security checks
  - Input sanitizers
- Documentation
  - Comprehensive README
  - Quick Start Guide
  - Example scripts
  - Configuration templates
- Testing
  - Unit tests for all converters
  - Integration tests
  - Pipeline tests
- Examples
  - Basic usage examples
  - Advanced LLM usage examples
  - Configuration examples

### Supported Models
- microsoft/phi-2 (2.7B)
- TinyLlama/TinyLlama-1.1B-Chat-v1.0 (1.1B)
- speakleash/Bielik-7B-v0.1 (7B - Polish)
- microsoft/phi-1_5 (1.3B)
- Custom HuggingFace models

### Dependencies
- transformers >= 4.30.0
- torch >= 2.0.0
- pydantic >= 2.0.0
- python-dotenv >= 1.0.0
- pyyaml >= 6.0

### Known Issues
- First model load takes time (downloading from HuggingFace)
- Large models (7B+) require significant RAM/GPU memory
- Some complex natural language queries may need fine-tuning

### Future Plans
- Support for more LLM models
- Text2Kubernetes converter
- Text2Terraform converter
- Web UI for interactive usage
- Plugin system for custom converters
- Improved context understanding
- Multi-language support improvements
- Caching for faster model loading

---

## Release Notes

### v0.1.0 - Initial Release

This is the first public release of NLP2CMD, a framework for converting natural language commands to executable code and configurations.

**Key Features:**
- 🤖 Small LLM support (1-3B parameters) for resource-efficient operation
- 🔧 Four main converters: text2env, text2bash, text2makefile, text2docker
- 🔗 Pipeline system for combining multiple operations
- 🔒 Security-first design with safe mode and validation
- 🇵🇱 Polish language support via Bielik model
- 📦 Easy installation and configuration

**Quick Start:**
```bash
pip install nlp2cmd
python -c "from nlp2cmd import Text2Bash; Text2Bash(dry_run=True).execute('pokaż pliki')"
```

**Feedback:**
We welcome feedback, bug reports, and feature requests! Please open an issue on GitHub.

---

[Unreleased]: https://github.com/softreck/nlp2cmd/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/softreck/nlp2cmd/releases/tag/v0.1.0
