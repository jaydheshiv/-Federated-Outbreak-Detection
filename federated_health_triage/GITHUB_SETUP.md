# GitHub Setup Instructions

## Step 1: Create a New GitHub Repository

1. Go to [GitHub.com](https://github.com/new)
2. Create a new repository with:
   - **Repository name**: `federated-health-triage`
   - **Description**: `AI-integrated Federated Learning Software for healthcare triage across multiple clinics`
   - **Visibility**: Public (for collaboration)
   - **Do NOT initialize** with README, .gitignore, or license (we have these)

## Step 2: Initialize Git and Push Code

```bash
# Navigate to project directory
cd federated_health_triage

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Federated Learning Health Triage System

- Implement federated learning framework with 3 clinic models
- Create data generation for synthetic health data
- Build model aggregation and ensemble system
- Add triage assessment engine with clinical rules
- Include comprehensive testing suite
- Add documentation and examples"

# Add remote repository (replace <username> with your GitHub username)
git remote add origin https://github.com/<username>/federated-health-triage.git

# Create main branch and push
git branch -M main
git push -u origin main
```

## Step 3: Create Additional Branches

```bash
# Create development branch
git checkout -b develop
git push -u origin develop

# Create feature branches for different components
git checkout -b feature/differential-privacy
git checkout -b feature/api-integration
git checkout -b feature/web-interface
```

## Step 4: Add Topics to Repository

On GitHub repository settings, add topics:
- `federated-learning`
- `machine-learning`
- `healthcare`
- `triage`
- `privacy`
- `ensemble-learning`
- `python`
- `healthcare-ai`

## Step 5: Configure Repository Settings

### Branch Protection Rules
1. Go to Settings → Branches
2. Add rule for `main` branch:
   - ✓ Require pull request reviews before merging
   - ✓ Require branches to be up to date
   - ✓ Include administrators
   - ✓ Require status checks to pass

### Enable Features
1. Settings → Features
   - ✓ Discussions
   - ✓ Projects
   - ✓ Wiki
   - ✓ Issues

## Step 6: Add GitHub Actions CI/CD

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8
    
    - name: Lint with flake8
      run: |
        # Stop the build if there are Python syntax errors
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Run tests with pytest
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Step 7: Add Repository Badges (Update README.md)

Add these badges to your README:

```markdown
[![Tests](https://github.com/<username>/federated-health-triage/workflows/Tests/badge.svg)](https://github.com/<username>/federated-health-triage/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

## Step 8: Setup GitHub Pages Documentation

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install mkdocs mkdocs-material
    
    - name: Build documentation
      run: |
        mkdocs build
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site
```

## Step 9: Create Release

```bash
# Create a git tag for version 1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0: Federated Learning Health Triage System"

# Push tags to GitHub
git push origin v1.0.0

# Or push all tags
git push origin --tags
```

On GitHub:
1. Go to Releases
2. Click "Create a new release"
3. Select tag `v1.0.0`
4. Add release notes
5. Attach any binaries if needed
6. Click "Publish release"

## Step 10: Collaborate & Contribution Guide

1. Update CONTRIBUTING.md with specific instructions
2. Create issue templates in `.github/ISSUE_TEMPLATE/`
3. Create PR templates in `.github/pull_request_template.md`

### Issue Template (`.github/ISSUE_TEMPLATE/bug_report.md`)
```markdown
---
name: Bug report
about: Create a report to help us improve
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. ...
2. ...

**Expected behavior**
Description of what you expected to happen.

**Environment**
- OS: [e.g. Windows, Linux]
- Python version: [e.g. 3.9]
- Package versions: [output of pip freeze]
```

### PR Template (`.github/pull_request_template.md`)
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## Testing
- [ ] Added tests
- [ ] All tests pass
- [ ] No new warnings

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added where needed
- [ ] Documentation updated
```

## Step 11: Enable Additional Features

### Enable Discussions
Settings → Discussions → Enable discussions

### Setup Project Board
1. Projects tab → Create new project
2. Name: "Development Roadmap"
3. Use automated kanban template
4. Add cards for tasks

### Create Wiki
1. Wiki tab
2. Create "Home" page with overview
3. Create "Installation" page
4. Create "API Reference" page

## Useful GitHub Commands

```bash
# Clone the repository
git clone https://github.com/<username>/federated-health-triage.git

# Create and switch to feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin feature/my-feature

# Create pull request (from GitHub UI)

# After PR merge, update local
git checkout main
git pull origin main

# Clean up merged branches
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

## Repository URL

After setup, your repository will be available at:
```
https://github.com/<username>/federated-health-triage
```

## Recommended .gitignore Files to Add

Already included in `.gitignore`, but key ones:
- `__pycache__/`
- `*.py[cod]`
- `*.egg-info/`
- `venv/`
- `*.pkl` (models)
- `*.csv` (data)
- `.vscode/`
- `.idea/`

---

## Quick Reference: Git Workflow

```
1. Create branch:    git checkout -b feature/name
2. Make changes:     Edit files
3. Stage changes:    git add .
4. Commit changes:   git commit -m "Description"
5. Push branch:      git push origin feature/name
6. Create PR:        GitHub UI
7. Merge PR:         GitHub UI (after approval)
8. Delete branch:    git branch -d feature/name
9. Update local:     git pull origin main
```

---

For more information, see:
- [GitHub Docs](https://docs.github.com)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Actions](https://github.com/features/actions)
