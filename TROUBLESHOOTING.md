# Troubleshooting Guide

## Common Issues and Solutions

### GitHub Actions Issues

#### Issue: Workflow not triggering
**Symptoms:**
- Push to branch but workflow doesn't run
- No workflow runs visible in Actions tab

**Solutions:**
1. Check workflow file syntax
```bash
# Validate YAML syntax
python -m yaml .github/workflows/ci-cd.yml
```

2. Verify branch names match triggers
```yaml
on:
  push:
    branches: [ main, develop ]  # Must match your branch names exactly
```

3. Check if Actions are enabled
- Go to repository Settings → Actions → General
- Ensure "Allow all actions and reusable workflows" is selected

4. Look for workflow file in correct location
```
.github/
└── workflows/
    ├── ci-cd.yml
    ├── security.yml
    └── code-quality.yml
```

---

#### Issue: Workflow fails with "Permission denied"
**Symptoms:**
- Error: "Resource not accessible by integration"
- Steps fail with permission errors

**Solutions:**
1. Update workflow permissions
```yaml
permissions:
  contents: read
  packages: write
  security-events: write
```

2. Check repository settings
- Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"

3. For protected branches
- Settings → Branches → Branch protection rules
- Allow workflows to push to protected branches

---

#### Issue: Secrets not found
**Symptoms:**
- Error: "Secret XXXXXX not found"
- Authentication failures

**Solutions:**
1. Verify secret name matches exactly (case-sensitive)
```yaml
# Wrong
${{ secrets.github_token }}

# Correct
${{ secrets.GITHUB_TOKEN }}
```

2. Check secret scope
- Repository secrets: Available to all workflows
- Environment secrets: Only available when environment specified
- Organization secrets: Check if repository has access

3. Test secret availability
```yaml
- name: Check secrets
  run: |
    if [ -z "${{ secrets.MY_SECRET }}" ]; then
      echo "Secret is not set"
      exit 1
    fi
```

---

### Docker Issues

#### Issue: Docker build fails
**Symptoms:**
- "No such file or directory" errors
- "Cannot find module" errors

**Solutions:**
1. Check COPY paths in Dockerfile
```dockerfile
# Make sure files exist at these paths
COPY requirements.txt .
COPY . .
```

2. Verify .dockerignore isn't excluding required files
```bash
# List what's being sent to Docker context
docker build --no-cache -t test . 2>&1 | grep "Sending build context"
```

3. Check for Windows/Linux line ending issues
```bash
# Convert to Unix line endings
dos2unix Dockerfile
```

4. Use BuildKit for better error messages
```bash
DOCKER_BUILDKIT=1 docker build -t myapp .
```

---

#### Issue: Container exits immediately
**Symptoms:**
- Container starts then stops
- "docker ps" shows no running containers

**Solutions:**
1. Check application logs
```bash
docker logs <container_id>
```

2. Run container interactively
```bash
docker run -it myapp /bin/bash
```

3. Check CMD/ENTRYPOINT syntax
```dockerfile
# Wrong (shell form doesn't handle signals properly)
CMD python app.py

# Correct (exec form)
CMD ["python", "app.py"]
```

4. Verify application is listening on correct port
```python
# Ensure using 0.0.0.0 not localhost
app.run(host='0.0.0.0', port=8000)
```

---

#### Issue: Port already in use
**Symptoms:**
- "address already in use" error
- Cannot bind to port

**Solutions:**
1. Find and kill process using port
```bash
# Find process
lsof -i :8000
# or
netstat -ano | findstr :8000

# Kill process
kill -9 <PID>
```

2. Use different port mapping
```bash
docker run -p 8001:8000 myapp
```

3. Stop all containers
```bash
docker-compose down
docker stop $(docker ps -aq)
```

---

### Testing Issues

#### Issue: Tests pass locally but fail in CI
**Symptoms:**
- "pytest" succeeds on local machine
- Same tests fail in GitHub Actions

**Solutions:**
1. Check Python version consistency
```yaml
# In workflow
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Must match local version
```

2. Verify all dependencies installed
```bash
# Add to workflow
- name: Debug dependencies
  run: pip freeze
```

3. Check for environment-specific issues
```python
# Add to conftest.py
import os
print(f"Running in: {os.getenv('GITHUB_ACTIONS', 'local')}")
```

4. Ensure test isolation
```python
# Use fixtures to reset state
@pytest.fixture(autouse=True)
def reset_database():
    # Setup
    setup_test_db()
    yield
    # Teardown
    cleanup_test_db()
```

---

#### Issue: Tests are flaky
**Symptoms:**
- Tests sometimes pass, sometimes fail
- Intermittent failures

**Solutions:**
1. Identify timing issues
```python
# Add explicit waits
import time
time.sleep(1)  # Temporary debugging

# Better: use retry logic
from tenacity import retry, stop_after_attempt
@retry(stop=stop_after_attempt(3))
def test_api_call():
    ...
```

2. Check for test order dependencies
```bash
# Run in random order
pytest --random-order
```

3. Increase timeouts
```python
# In pytest.ini
[pytest]
timeout = 300
```

---

### Deployment Issues

#### Issue: Deployment succeeds but app doesn't work
**Symptoms:**
- Deployment workflow completes successfully
- Application returns errors or doesn't respond

**Solutions:**
1. Check application logs
```bash
# For Kubernetes
kubectl logs deployment/python-web-app

# For Docker
docker logs <container_id>

# For cloud services
# AWS: CloudWatch
# Azure: Log Analytics
# GCP: Cloud Logging
```

2. Verify environment variables
```bash
# Print environment (without sensitive values)
printenv | grep -v SECRET | grep -v PASSWORD
```

3. Check health endpoint
```bash
curl -v https://myapp.com/health
```

4. Verify database connectivity
```python
# Add to health check
@app.route('/health')
def health():
    try:
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'database': 'connected'}
    except:
        return {'status': 'unhealthy', 'database': 'disconnected'}, 503
```

---

#### Issue: Database migrations fail
**Symptoms:**
- "Table already exists" errors
- "Column not found" errors

**Solutions:**
1. Check migration order
```bash
# For Alembic
alembic history
alembic current

# For Django
python manage.py showmigrations
```

2. Reset migrations (development only!)
```bash
# Drop all tables and rerun
python manage.py migrate --fake-initial
```

3. Add migration checks to deployment
```yaml
- name: Run migrations
  run: |
    python manage.py migrate --check
    python manage.py migrate --no-input
```

---

### Performance Issues

#### Issue: Slow build times
**Solutions:**
1. Enable caching
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

2. Use Docker layer caching
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

3. Parallelize tests
```bash
pytest -n auto  # Uses pytest-xdist
```

---

#### Issue: High memory usage
**Solutions:**
1. Set resource limits
```yaml
# In docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 512M
```

2. Profile memory usage
```python
import tracemalloc
tracemalloc.start()
# Your code
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

---

## Debugging Commands

### GitHub Actions
```bash
# Download workflow logs
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id> --failed

# List recent runs
gh run list
```

### Docker
```bash
# Inspect container
docker inspect <container_id>

# Check resource usage
docker stats

# View container processes
docker top <container_id>

# Copy files from container
docker cp <container_id>:/path/to/file ./local-path
```

### Python
```bash
# Run with verbose output
python -v app.py

# Check module path
python -c "import sys; print(sys.path)"

# Profile code
python -m cProfile -o profile.stats app.py

# Memory profiling
python -m memory_profiler app.py
```

---

## Getting Help

### Before asking for help, collect:
1. Full error message
2. Workflow logs (if applicable)
3. Docker/application logs
4. Steps to reproduce
5. Environment details (OS, Python version, etc.)

### Resources:
- GitHub Actions docs: https://docs.github.com/en/actions
- Docker docs: https://docs.docker.com/
- Python debugging: https://docs.python.org/3/library/debug.html
- Stack Overflow with tags: `github-actions`, `docker`, `pytest`

---

## Emergency Procedures

### Rollback Deployment
```bash
# Kubernetes
kubectl rollout undo deployment/python-web-app

# Docker Compose
docker-compose down
git checkout <previous-commit>
docker-compose up -d

# AWS ECS
aws ecs update-service --cluster prod --service app --task-definition app:previous-version
```

### Stop All Workflows
1. Go to repository Actions tab
2. Click on running workflow
3. Click "Cancel workflow"

### Disable Deployments
1. Settings → Environments → [environment-name]
2. Add yourself as required reviewer (stops auto-deployments)
