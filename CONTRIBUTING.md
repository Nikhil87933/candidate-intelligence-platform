# Contributing

Thank you for contributing to this project.

## Development Setup

Clone the repository.

```bash
git clone <repository-url>
cd candidate-intelligence-platform
```

Create and activate a virtual environment.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
make install
```

---

## Before Opening a Pull Request

Run:

```bash
make check
```

Ensure:

- Ruff passes
- Black passes
- mypy passes
- pytest passes

---

## Branching Strategy

Create a feature branch from `main`.

```bash
git checkout -b feature/<feature-name>
```

Do not commit directly to `main`.

---

## Commit Messages

Follow Conventional Commits.

Examples:

```
feat: add authentication
fix: correct Docker build
docs: update README
test: add unit tests
refactor: simplify pipeline
chore: update dependencies
```

---

## Pull Requests

Every Pull Request should:

- Pass CI
- Include a clear description
- Be focused on a single change
- Be reviewed before merging

---

## Code Style

This project uses:

- Ruff
- Black
- mypy
- pytest
- pre-commit

Please do not bypass these checks.
