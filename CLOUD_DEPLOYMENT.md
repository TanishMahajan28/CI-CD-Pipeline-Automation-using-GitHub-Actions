# Cloud Deployment Guide

This guide covers deploying your Python web application to major cloud providers.

## Table of Contents
- [AWS Deployment](#aws-deployment)
- [Azure Deployment](#azure-deployment)
- [Google Cloud Platform](#google-cloud-platform)
- [DigitalOcean](#digitalocean)
- [Heroku](#heroku)

---

## AWS Deployment

### Option 1: AWS Elastic Container Service (ECS)

#### Prerequisites
- AWS Account
- AWS CLI installed and configured
- Docker image in ECR (Elastic Container Registry)

#### Setup Steps

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name python-web-app --region us-east-1
```

2. **Update GitHub Secrets**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REPOSITORY`

3. **Add to GitHub Actions workflow**
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ${{ secrets.AWS_REGION }}

- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build and push to ECR
  env:
    ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
    ECR_REPOSITORY: python-web-app
    IMAGE_TAG: ${{ github.sha }}
  run: |
    docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
    docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

- name: Deploy to ECS
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: task-definition.json
    service: python-web-app-service
    cluster: production-cluster
    wait-for-service-stability: true
```

### Option 2: AWS Elastic Beanstalk

```yaml
- name: Deploy to Elastic Beanstalk
  uses: einaregilsson/beanstalk-deploy@v21
  with:
    aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    application_name: python-web-app
    environment_name: production
    version_label: ${{ github.sha }}
    region: us-east-1
    deployment_package: deploy.zip
```

### Option 3: AWS Lambda (Serverless)

For serverless deployment with AWS Lambda + API Gateway:

```yaml
- name: Deploy to Lambda
  run: |
    pip install -r requirements.txt -t package/
    cd package && zip -r ../deployment-package.zip .
    cd ..
    zip -g deployment-package.zip app.py
    aws lambda update-function-code \
      --function-name python-web-app \
      --zip-file fileb://deployment-package.zip
```

---

## Azure Deployment

### Azure Container Apps

#### Prerequisites
- Azure Account
- Azure CLI installed

#### Setup Steps

1. **Create Azure Service Principal**
```bash
az ad sp create-for-rbac --name "github-actions" --role contributor \
    --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
    --sdk-auth
```

2. **Update GitHub Secrets**
- `AZURE_CREDENTIALS` (JSON output from above command)
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`

3. **Add to GitHub Actions workflow**
```yaml
- name: Login to Azure
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}

- name: Build and push to Azure Container Registry
  uses: azure/docker-login@v1
  with:
    login-server: myregistry.azurecr.io
    username: ${{ secrets.ACR_USERNAME }}
    password: ${{ secrets.ACR_PASSWORD }}

- name: Build and push Docker image
  run: |
    docker build -t myregistry.azurecr.io/python-web-app:${{ github.sha }} .
    docker push myregistry.azurecr.io/python-web-app:${{ github.sha }}

- name: Deploy to Azure Container Apps
  uses: azure/container-apps-deploy-action@v1
  with:
    containerAppName: python-web-app
    resourceGroup: ${{ secrets.AZURE_RESOURCE_GROUP }}
    imageToDeploy: myregistry.azurecr.io/python-web-app:${{ github.sha }}
```

### Azure App Service

```yaml
- name: Deploy to Azure Web App
  uses: azure/webapps-deploy@v2
  with:
    app-name: python-web-app
    publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
    images: myregistry.azurecr.io/python-web-app:${{ github.sha }}
```

---

## Google Cloud Platform

### Cloud Run Deployment

#### Prerequisites
- GCP Account
- gcloud CLI installed
- Service Account with necessary permissions

#### Setup Steps

1. **Create Service Account and Key**
```bash
gcloud iam service-accounts create github-actions
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:github-actions@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"
```

2. **Update GitHub Secrets**
- `GCP_PROJECT_ID`
- `GCP_SERVICE_ACCOUNT_KEY` (JSON key file content)

3. **Add to GitHub Actions workflow**
```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

- name: Set up Cloud SDK
  uses: google-github-actions/setup-gcloud@v2

- name: Configure Docker for GCR
  run: gcloud auth configure-docker

- name: Build and push to GCR
  env:
    PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
    IMAGE_NAME: python-web-app
  run: |
    docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME:${{ github.sha }} .
    docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:${{ github.sha }}

- name: Deploy to Cloud Run
  run: |
    gcloud run deploy python-web-app \
      --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/python-web-app:${{ github.sha }} \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated
```

---

## DigitalOcean

### App Platform Deployment

#### Setup Steps

1. **Update GitHub Secrets**
- `DIGITALOCEAN_ACCESS_TOKEN`

2. **Add to GitHub Actions workflow**
```yaml
- name: Install doctl
  uses: digitalocean/action-doctl@v2
  with:
    token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

- name: Build and push to DOCR
  run: |
    doctl registry login
    docker build -t registry.digitalocean.com/myregistry/python-web-app:${{ github.sha }} .
    docker push registry.digitalocean.com/myregistry/python-web-app:${{ github.sha }}

- name: Deploy to App Platform
  run: |
    doctl apps create-deployment ${{ secrets.APP_ID }} --wait
```

### Droplet Deployment (via SSH)

```yaml
- name: Deploy to Droplet
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.DROPLET_HOST }}
    username: ${{ secrets.DROPLET_USER }}
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      cd /var/www/python-web-app
      git pull origin main
      docker-compose down
      docker-compose pull
      docker-compose up -d
```

---

## Heroku

### Setup Steps

1. **Update GitHub Secrets**
- `HEROKU_API_KEY`
- `HEROKU_APP_NAME`
- `HEROKU_EMAIL`

2. **Add to GitHub Actions workflow**
```yaml
- name: Deploy to Heroku
  uses: akhileshns/heroku-deploy@v3.12.14
  with:
    heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
    heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
    heroku_email: ${{ secrets.HEROKU_EMAIL }}
    usedocker: true
```

3. **Create heroku.yml**
```yaml
build:
  docker:
    web: Dockerfile
run:
  web: gunicorn app:app
```

---

## Best Practices

### 1. Environment-Specific Configuration
```yaml
# Use different configs for staging vs production
- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  env:
    CONFIG: production
  run: ./deploy.sh

- name: Deploy to Staging
  if: github.ref == 'refs/heads/develop'
  env:
    CONFIG: staging
  run: ./deploy.sh
```

### 2. Health Checks
Always implement health checks and wait for them:
```yaml
- name: Wait for deployment
  run: |
    sleep 30
    curl -f https://myapp.com/health || exit 1
```

### 3. Rollback Strategy
```yaml
- name: Rollback on failure
  if: failure()
  run: |
    # Your rollback commands here
    kubectl rollout undo deployment/python-web-app
```

### 4. Notifications
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Troubleshooting

### Common Issues

**Authentication Failures**
- Verify all secrets are correctly set
- Check service account permissions
- Ensure tokens haven't expired

**Deployment Timeouts**
- Increase timeout values in workflow
- Check application startup time
- Review container resource limits

**Image Not Found**
- Verify registry URL
- Check authentication to registry
- Ensure image was successfully pushed

---

## Cost Optimization

1. **Use caching** for Docker layers
2. **Implement auto-scaling** based on traffic
3. **Use spot/preemptible instances** for non-production
4. **Clean up old images** regularly
5. **Right-size resources** based on actual usage

---

## Security Checklist

- [ ] Use secrets for all sensitive data
- [ ] Implement least-privilege access
- [ ] Enable HTTPS/TLS
- [ ] Set up WAF (Web Application Firewall)
- [ ] Enable logging and monitoring
- [ ] Use private networks where possible
- [ ] Implement rate limiting
- [ ] Regular security updates
