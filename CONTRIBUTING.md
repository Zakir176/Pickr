# Contributing to Pickr

Thank you for your interest in contributing to Pickr! We appreciate your help in making photo curation faster and easier.

## 🛠️ Development Workflow

1.  **Fork the repository** and create your branch from `main`.
2.  **Set up the environment** (refer to the [README.md](README.md) Quick Start).
3.  **Make your changes**, ensuring they follow the project's style and quality standards.
4.  **Lint your code** before submitting.
5.  **Run tests** to ensure no regressions were introduced.

## 📏 Style Guidelines

### Python (Backend)
-   Follow **PEP 8** standards.
-   Use **Black** for formatting.
-   Check your code with **Flake8**:
    ```sh
    flake8 main.py analysis.py ..\test_scoring.py --max-line-length=120
    ```

### JavaScript/Vue (Frontend)
-   Follow **Vue Style Guide** (Priority A/B).
-   Use **ESLint** (Flat Config) for linting:
    ```sh
    npm run lint
    ```
-   Components should be written in **SFC (Single File Component)** format with `<script setup>`.

## 🧪 Testing

### Backend
We use **pytest**. Before submitting a pull request, ensure all tests pass:
```sh
pytest test_scoring.py
```

### Frontend
Run a production build to check for compilation errors:
```sh
npm run build
```

## 🚀 Pull Request Process
1.  Ensure all linting and tests pass.
2.  Update the documentation if you are adding new features.
3.  Provide a clear and concise description of your changes in the PR.
