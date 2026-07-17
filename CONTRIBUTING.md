# Contributing to Smart Stadium Operations AI

Thank you for your interest in contributing to the Smart Stadium Operations AI project! Follow these guidelines to ensure a smooth contribution process.

---

## 🛠️ Project Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rroshan-cell/smart-stadium-operations-ai.git
   cd smart-stadium-operations-ai
   ```

2. **Install Dependencies**:
   Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and configure your API keys:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   AI_MODEL=llama-3.3-70b-versatile
   ```

---

## 🌿 Branch Naming

Use descriptive branch names prefixed with the category of change:
- `feature/` for new features (e.g., `feature/dynamic-egress-routes`)
- `bugfix/` for bug fixes (e.g., `bugfix/rate-limit-leak`)
- `docs/` for documentation updates (e.g., `docs/add-api-flow`)
- `refactor/` for code restructuring (e.g., `refactor/exception-masking`)

---

## 💬 Commit Messages

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation updates
- `style:` for code formatting adjustments
- `refactor:` for code restructuring
- `test:` for adding or modifying tests

*Example*: `feat: integrate groq client request timeouts`

---

## 🧪 Testing

All contributions must include tests where applicable. We maintain a strict **94% coverage threshold**.
- Run the full test suite locally before pushing:
  ```bash
  python -m pytest --cov=. --cov-report=term-missing
  ```
- All tests must run **offline** and remain **deterministic** using mock objects.

---

## 🎨 Code Style

- **Python**: Follow PEP 8 guidelines. Use type hints for all function arguments and return signatures.
- **Frontend CSS/JS**: Use Vanilla JavaScript (ES6 Modules) and standard CSS variables. Avoid adding third-party frameworks.
- **Clean Code**: Keep functions single-purpose, remove dead/unused code, and maintain existing docstring formats.

---

## 🚀 Pull Requests

1. Create your branch from `main`.
2. Ensure linting and tests pass locally.
3. Open a Pull Request with a clear title and description of the change.
4. Verify that the GitHub Actions CI workflow runs successfully.

---

## 🐛 Issue Reporting

If you encounter bugs, security vulnerabilities, or have suggestions:
1. Search existing issues to avoid duplicates.
2. File a new issue using the project template.
3. Include details of your environment, steps to reproduce, and expected vs. actual behavior.
