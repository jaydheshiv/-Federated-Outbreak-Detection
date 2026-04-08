# Contributing to Federated Health Triage System

Thank you for considering contributing to the Federated Health Triage System!

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct.

## How Can I Contribute?

### Reporting Bugs
Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Include code samples** if possible
* **Describe the exact steps** which reproduce the problem
* **Provide specific examples** to demonstrate the steps
* **Describe the behavior** you observed and point out what exactly is the problem
* **Include details about your environment** (Python version, OS, etc.)

### Suggesting Enhancements
Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **A clear and descriptive title**
* **A step-by-step description** of the suggested enhancement
* **Specific examples** to demonstrate the steps
* **Describe the current behavior** and **explain the expected behavior**
* **Explain why this enhancement** would be useful

### Pull Requests

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/federated_health_triage.git
cd federated_health_triage

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Test specific function
python -m pytest tests/test_system.py::TestClinicModel::test_model_training -v
```

## Code Style

We follow PEP 8. Please ensure your code adheres to these standards:

```bash
# Format code with Black
black .

# Check with flake8
flake8 .

# Fix style issues
autopep8 --in-place --aggressive --aggressive *.py
```

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add support for differential privacy in aggregation

- Implement Laplace mechanism
- Add privacy parameters to config
- Add tests for privacy guarantees

Closes #123
```

## Documentation

- Update README.md if you change functionality
- Add docstrings to new functions/classes
- Update ADVANCED_SETUP.md for complex features
- Include examples in docstrings

## Release Process

Maintainers will handle versioning using semantic versioning (MAJOR.MINOR.PATCH).

---

Thank you for your contribution! 🎉
