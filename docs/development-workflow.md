# Development Workflow

## Branch Strategy

The `main` branch must remain stable and deployable.

Do not develop directly on `main`.

Use short-lived branches:

- `feature/<name>` - new functionality
- `fix/<name>` - bug fixes
- `refactor/<name>` - code restructuring
- `docs/<name>` - documentation changes
- `test/<name>` - test changes
- `chore/<name>` - tooling, CI, maintenance

Examples:

- `feature/postgres-persistence`
- `feature/minio-object-storage`
- `feature/qdrant-vector-search`
- `feature/document-extraction`
- `fix/pdf-upload-validation`
- `chore/repository-workflow`

## Development Cycle

1. Update local `main`.
2. Create a branch from `main`.
3. Implement one focused change.
4. Run local quality checks.
5. Commit using a conventional commit message.
6. Push the branch.
7. Open a pull request into `main`.
8. Wait for CI to pass.
9. Review the changes.
10. Merge into `main`.
11. Delete the feature branch.

## Local Quality Gate

Before opening a pull request, run:

    make check

The project quality gate includes:

- Ruff linting
- Black format checking
- MyPy type checking
- Pytest tests

Pre-commit hooks provide additional checks during commits.

## Commit Convention

Use concise conventional commits:

- `feat: add candidate repository`
- `fix: handle invalid PDF files`
- `test: add document extraction tests`
- `docs: update architecture documentation`
- `refactor: simplify ingestion service`
- `chore: update CI workflow`

## Pull Requests

Each pull request should:

- Have one focused purpose
- Target `main`
- Pass CI
- Include tests where applicable
- Avoid unrelated changes
- Use the repository PR template

## Main Branch

The `main` branch is the stable integration branch.

Application code changes should reach `main` through pull requests.
