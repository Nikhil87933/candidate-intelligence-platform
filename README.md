# Enterprise Python Template

A reusable, production-ready Python project template that follows modern software engineering practices used in professional development teams.

---

## Features

- Python 3.12
- Modern `pyproject.toml`
- `src/` project layout
- Virtual environment support
- Ruff linting
- Black formatting
- mypy type checking
- pytest testing
- pre-commit hooks
- GitHub Actions CI
- Branch protection ready
- Pull Request template
- Issue templates
- CODEOWNERS
- Dependabot
- Docker support

---

## Project Structure

```
.
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   └── pull_request_template.md
├── docs/
├── scripts/
├── src/
├── tests/
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

---

## Quick Start

Clone the repository.

```bash
git clone <repository-url>
cd enterprise-python-template
```

Create a virtual environment.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
make install
```

Run all quality checks.

```bash
make check
```

Format the code.

```bash
make format
```

Run tests.

```bash
make test
```

---

## Docker

Build the image.

```bash
docker build -t enterprise-python-template:0.1 .
```

Run the container.

```bash
docker run --rm enterprise-python-template:0.1
```

---

## Continuous Integration

GitHub Actions automatically runs:

- Ruff
- Black
- mypy
- pytest

on every Pull Request.

---

## Development Workflow

1. Create a feature branch.
2. Make changes.
3. Commit with pre-commit hooks.
4. Push the branch.
5. Open a Pull Request.
6. Wait for CI to pass.
7. Merge into `main`.

---

## License

MIT License.

Repository workflow is validated through pull requests and CI checks.
