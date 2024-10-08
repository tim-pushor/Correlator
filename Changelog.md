# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project will adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html),
once its public API is documented.

## [0.0.4-PRE] - 2024-08-28

### Added

- Docker support
- Transmission module
- Email handler with mako template rendering (EARLY)
- Twilio handler (EARLY)
- JSON based app configuration with dynamic loading
- Runtime configuration store
- Openssh container to test/demo openssh module
- keyring support for secrets (EARLY)

### Changed

- Simplified events

### Deprecated

- all documents in docs/

- ## [0.0.3] - 2023-03-01

### Added

- Release to GitHub
- Secure Shell login Module
- Syslog server CLI
- CounterOverTime utility class
- Caputil CLI utility
- Initial docs

### Fixed
- lots of stuff

### Removed
- GlobalConfig class

## [0.0.2] - 2023-02-19

### Added
- Started documenting code
- Syslog trailer (record separator) discovery.
- Some captured syslog/linux data

### Changed
- Transition from SocketServer
- Changed formats to f-strings

### Fixed
- Logging
- Structured data parsing

### Removed
- All code for proprietary systems.

## [0.0.1] - 2023-02-13

### Added

- Python package
- Module & Event system
- README.md
- Example CLI's that process log files as well as syslog data.
- Extensions and modules support logs from proprietary system.

