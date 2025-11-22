# Deployment Guide

## Quick Deploy Options

### 1. Heroku

```bash
# Install Heroku CLI
heroku login
heroku create your-app-name
git push heroku main
```

The `Procfile` is already configured.

### 2. Docker (Local/Cloud)

```bash
# Build image
docker build -t tourism-ai .

# Run container
docker run -p 5000:5000 tourism-ai

# Or use Docker Compose
docker-compose up
```

### 3. Railway

1. Connect your GitHub repository
2. Railway will auto-detect the Dockerfile
3. Deploy!

### 4. Render

1. Create a new Web Service
2. Connect your repository
3. Use these settings:
   - Build Command: `docker build -t tourism-ai .`
   - Start Command: `docker run -p $PORT:5000 tourism-ai`
   - Or use: `gunicorn --bind 0.0.0.0:$PORT app:app`

### 5. Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/tourism-ai
gcloud run deploy --image gcr.io/PROJECT_ID/tourism-ai --platform managed
```

### 6. AWS Elastic Beanstalk

1. Install EB CLI
2. `eb init`
3. `eb create`
4. Deploy!

## Environment Variables

No environment variables are required. The application uses public APIs.

## Health Check

All deployments should configure health checks to:
```
GET /health
```

## Port Configuration

- Default port: `5000`
- For platforms like Heroku/Railway, use `$PORT` environment variable (already configured in Procfile)

