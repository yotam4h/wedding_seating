# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-09-29

### Added
- Guest seating optimizer with VIP, group, and friend heuristics.
- CSV importer, CSV/PDF exporters, and Matplotlib visualization helpers.
- Command-line interface (`python -m wedding_seating` / `wedding-seating`).
- Unit tests for core optimizer, utilities, and CLI behavior.
- Project documentation outlining features, installation, and usage.
- Packaging metadata (`setup.py`, console entry point) and project `.gitignore`.

### Changed
- Hardened local optimization swap routine to avoid duplicate assignments.
- Added comprehensive type hints across the codebase for better tooling support.

[0.1.0]: https://github.com/yotam4h/wedding_seating/releases/tag/v0.1.0
