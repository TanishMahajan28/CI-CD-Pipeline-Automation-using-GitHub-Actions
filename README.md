# CI/CD Pipeline Setup Guide

## 📋 Overview

This repository contains a complete CI/CD pipeline setup for a Python web application using GitHub Actions, Docker, and cloud integration.

### Features
- ✅ Automated build, test, and deployment workflows
- ✅ Docker containerization with multi-stage builds
- ✅ Comprehensive testing with pytest and coverage reports
- ✅ Code quality checks (linting, formatting)
- ✅ Separate staging and production environments
- ✅ Security best practices

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git
- GitHub account

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

### Using Docker

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f web
   ```

3. **Stop containers**
   ```bash
   docker-compose down
   ```

## 🔧 CI/CD Pipeline Configuration

### GitHub Actions Workflow

The pipeline consists of 4 main jobs:

1. **Build and Test** - Runs on all pushes and PRs
   - Sets up Python environment
   - Installs dependencies
   - Runs linting (flake8)
   - Executes test suite with coverage
   - Uploads coverage reports

2. **Build Docker** - Runs on pushes to main/develop
   - Builds Docker image
   - Pushes to GitHub Container Registry
   - Tags appropriately based on branch

3. **Deploy Staging** - Runs on pushes to develop
   - Deploys to staging environment
   - Runs smoke tests

4. **Deploy Production** - Runs on pushes to main
   - Deploys to production environment
   - Runs health checks
   - Sends notifications

### Required GitHub Secrets

Configure these secrets in your repository settings (Settings → Secrets and variables → Actions):

#### Required Secrets
- `GITHUB_TOKEN` - Automatically provided by GitHub

#### Optional Secrets (based on your deployment target)
- **AWS**
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`

- **Azure**
  - `AZURE_CREDENTIALS`
  - `AZURE_SUBSCRIPTION_ID`

- **GCP**
  - `GCP_SERVICE_ACCOUNT_KEY`
  - `GCP_PROJECT_ID`

- **Generic**
  - `DEPLOY_SSH_KEY` - For SSH deployments
  - `DEPLOY_HOST` - Deployment server address
  - `SLACK_WEBHOOK_URL` - For notifications

### Setting Up Environments

1. Go to your repository → Settings → Environments
2. Create two environments: `staging` and `production`
3. For production, enable "Required reviewers" for manual approval
4. Add environment-specific secrets if needed

## 📝 Testing

### Run Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test markers
pytest -m unit
pytest -m integration

# Run specific test file
pytest tests/test_example.py
```

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── test_example.py      # Example tests
├── unit/                # Unit tests
├── integration/         # Integration tests
└── e2e/                 # End-to-end tests
```

## 🐳 Docker Configuration

### Dockerfile Features
- Multi-stage build for smaller image size
- Non-root user for security
- Health check endpoint
- Optimized layer caching

### Build Docker Image Locally

```bash
# Build image
docker build -t python-web-app:latest .

# Run container
docker run -p 8000:8000 python-web-app:latest

# Run with environment variables
docker run -p 8000:8000 --env-file .env python-web-app:latest
```

## 🔐 Security Best Practices

- Never commit `.env` files or secrets
- Use GitHub Secrets for sensitive data
- Run containers as non-root user
- Scan dependencies regularly (`pip-audit`, `safety`)
- Use specific version tags for dependencies
- Enable Dependabot for automated updates
- Review and approve production deployments

## 📊 Monitoring and Observability

### Health Check Endpoint

Implement a `/health` endpoint in your application:

```python
@app.route('/health')
def health():
    return {'status': 'healthy', 'version': '1.0.0'}
```

### Logging

Configure structured logging:

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

## 🚢 Deployment Strategies

### Rolling Deployment
Update instances gradually to minimize downtime.

### Blue-Green Deployment
Maintain two identical environments, switch traffic after validation.

### Canary Deployment
Route small percentage of traffic to new version first.

## 🐛 Troubleshooting

### Common Issues

**Pipeline fails on linting**
```bash
# Run black to auto-format
black .

# Run isort to organize imports
isort .
```

**Docker build fails**
- Check Dockerfile syntax
- Verify all required files exist
- Clear Docker cache: `docker system prune -a`

**Tests fail in CI but pass locally**
- Check environment variables
- Verify Python version matches
- Review test isolation

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Packaging Guide](https://packaging.python.org/)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

[Add your license here]

## 👥 Contact

[Add contact information]

---

**Next Steps:**
1. Customize `app.py` for your web framework (Flask/FastAPI/Django)
2. Update deployment commands in `.github/workflows/ci-cd.yml`
3. Configure your cloud provider credentials
4. Set up monitoring and alerting
5. Enable branch protection rules
