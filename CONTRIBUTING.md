# Contributing to ITG Video Compressor

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to ITG Video Compressor. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## 🛠️ Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## 🐛 Bug Reports

**Great Bug Reports** tend to have:

-   A quick summary and/or background.
-   Steps to reproduce.
    -   Be specific! "Compressing a 4GB file" is better than "Compressing a big file".
-   What you expected would happen.
-   What actually happened.
-   Notes (possibly including why you think this might be happening, or stuff you tried that didn't work).

## 💡 Feature Requests

Feature requests are welcome! But take a moment to find out whether your idea fits with the scope and aims of the project. It's up to *you* to make a strong case to convince the project's developers of the merits of this feature.

## 💻 Development Process

1.  **Fork the repo** and create your branch from `main`.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the app**:
    ```bash
    python main.py
    ```
4.  **Make your changes**.
5.  **Run tests**:
    ```bash
    pytest tests/
    ```
6.  **Format your code** (We follow PEP 8).

## 📐 Coding Standards

-   **Architecture**: Please strictly follow the Modular Architecture described in `PROJECT_ARCHITECTURE.md`.
-   **UI**: All new UI components must be placed in `src/ui/widgets/`.
-   **Strict Separation**: Do not import `tkinter` classes inside `compressor.py`.
-   **Type Hinting**: Use Python type hints where possible.
-   **Docstrings**: Add docstrings to all new classes and methods.

## 🧪 Testing

We use `pytest`. All new features should be accompanied by a unit test in `tests/`.

## 📦 Pull Requests

-   Ensure the PR description clearly describes the problem and solution.
-   Include the relevant issue number if applicable.
-   Verify that all tests pass before submitting.

Thanks! ❤️
