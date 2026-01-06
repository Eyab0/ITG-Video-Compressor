# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
-   **Professional Documentation**: Added `PROJECT_ARCHITECTURE.md` and `CONTRIBUTING.md`.
-   **Integration Tests**: Added `tests/test_refactor_structure.py`.

## [1.1.0] - 2026-01-04

### Changed
-   **Refactoring**: Complete rewrite of `src/app.py` into a modular architecture.
    -   Extracted `Header`, `FileList`, `SettingsPanel`, `ActionBar`, `StatusPanel` into `src/ui/widgets/`.
    -   Moved theme logic to `src/ui/styles.py`.
    -   Moved asset logic to `src/utils/assets.py`.
    -   Moved Google Drive logic to `src/utils/drive_importer.py`.

### Fixes
-   Fixed `gdown` dependency issues in PyInstaller builds.
-   Fixed UI freeze during large file compression by enforcing threading.

## [1.0.0] - 2025-12-25

### Added
-   Initial release.
-   Core video compression using `moviepy`.
-   Dark/Light mode toggle.
-   Batch processing queue.
