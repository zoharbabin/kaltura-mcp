# CI/CD with Kaltura MCP

This guide explains how to use the Continuous Integration and Continuous Deployment (CI/CD) workflow with the Kaltura MCP project.

## Overview

The Kaltura MCP project uses GitHub Actions for CI/CD. The workflow is designed to:

1. Run tests on multiple Python versions
2. Perform code quality checks
3. Build and test the Docker image
4. Generate and upload code coverage reports

## GitHub Actions Workflow

The workflow is defined in `.github/workflows/ci.yml` and is triggered on:
- Push events to the `main` branch
- Pull request events targeting the `main` branch

### Workflow Structure

The workflow consists of two main jobs:

#### 1. Test Job

This job runs on Ubuntu and tests the code on multiple Python versions:

```yaml
test:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ['3.10', '3.11', '3.12']
```

The test job performs the following steps:

1. **Checkout Code**: Uses `actions/checkout@v3` to clone the repository
2. **Set up Python**: Uses `actions/setup-python@v4` to set up the specified Python version
3. **Install System Dependencies**: Installs required system packages like `libmagic1`
4. **Install Python Dependencies**: Uses the setup script to install project dependencies
5. **Run Tests**: Runs tests with linting, type checking, and coverage
6. **Upload Coverage Reports**: Uploads coverage reports to Codecov

#### 2. Docker Job

This job runs on Ubuntu and builds the Docker image:

```yaml
docker:
  runs-on: ubuntu-latest
  needs: test
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

The Docker job only runs when:
- The event is a push (not a pull request)
- The branch is `main`
- The test job has completed successfully

The Docker job performs the following steps:

1. **Checkout Code**: Uses `actions/checkout@v3` to clone the repository
2. **Build Docker Image**: Builds the Docker image using the Dockerfile
3. **Test Docker Image**: Runs a simple test to verify the image works correctly

## Setting Up CI/CD for Your Fork

If you fork the Kaltura MCP repository, you can set up the CI/CD workflow for your fork by:

1. Ensuring GitHub Actions is enabled for your repository
2. Adding any required secrets to your repository settings

### Required Secrets

The workflow doesn't require any secrets by default, but if you want to deploy the Docker image to a container registry, you might need to add secrets like:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password or access token

## Running Tests Locally

Before pushing changes, it's a good practice to run the same tests that will be run in the CI/CD workflow:

```bash
# Install development dependencies
python setup_kaltura_mcp.py --dev-deps

# Run tests with linting and type checking
python run_tests.py --lint --type-check

# Run tests with coverage
python run_tests.py --coverage
```

## Using the Setup Script in CI/CD

The CI/CD workflow uses the `setup_kaltura_mcp.py` script to install dependencies and configure the environment. The script is run with the following options:

```bash
python setup_kaltura_mcp.py --non-interactive --skip-venv --dev-deps --skip-tests
```

These options:
- Disable interactive prompts (`--non-interactive`)
- Skip virtual environment creation (`--skip-venv`) since GitHub Actions provides its own environment
- Install development dependencies (`--dev-deps`) needed for testing
- Skip running tests during setup (`--skip-tests`) since tests will be run separately

## Troubleshooting CI/CD Issues

If the CI/CD workflow fails, check the following:

### Linting Issues

Run linting checks locally to identify and fix issues:

```bash
python run_tests.py --lint
```

Common linting issues include:
- Unused imports
- Import sorting
- Line length
- Indentation

### Type Checking Issues

Run type checking locally to identify and fix issues:

```bash
python run_tests.py --type-check
```

Common type checking issues include:
- Missing type annotations
- Incompatible types
- Missing imports

### Test Failures

Run tests locally to identify and fix issues:

```bash
python run_tests.py
```

### Docker Build Issues

Build the Docker image locally to identify and fix issues:

```bash
docker build -t kaltura-mcp .
```

## Best Practices

1. **Run tests locally before pushing**: This saves time and reduces the number of failed CI runs
2. **Keep the CI/CD workflow up to date**: Update the workflow when adding new dependencies or changing the build process
3. **Monitor CI/CD runs**: Regularly check the status of CI/CD runs to catch issues early
4. **Use the setup script**: Use the setup script to ensure consistent environments across development, testing, and deployment

## Next Steps

After setting up CI/CD, you can:
- [Configure the Kaltura MCP server](../getting-started/configuration.md)
- [Use Docker for deployment](../getting-started/docker.md)
- [Learn how to use the Kaltura MCP server](../getting-started/quick-start.md)