# Deployment Guide 🚀

This guide covers different deployment strategies for the AI Chatbot application.

## 📋 Pre-deployment Checklist

- [ ] OpenAI API key obtained
- [ ] Environment variables configured
- [ ] Dependencies installed and tested locally
- [ ] Docker setup tested (if using containers)
- [ ] Frontend build process verified
- [ ] Backend health check working

## 🐳 Docker Deployment (Recommended)

### Local Development with Docker Compose

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Chatbot
   ```

2. **Set up environment variables**
   ```bash
   # Copy backend config
   cp Backend/config.example Backend/.env
   # Edit Backend/.env with your OpenAI API key
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   The application will be available at:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

### Production Docker Deployment

1. **Build images**
   ```bash
   # Backend
   docker build -t chatbot-backend ./Backend
   
   # Frontend
   docker build -t chatbot-frontend ./Frontend
   ```

2. **Run containers**
   ```bash
   # Backend
   docker run -d \
     --name chatbot-backend \
     -p 8000:8000 \
     -e OPENAI_API_KEY=your_key_here \
     -e CORS_ORIGINS=https://your-frontend-domain.com \
     chatbot-backend

   # Frontend
   docker run -d \
     --name chatbot-frontend \
     -p 3000:3000 \
     -e NEXT_PUBLIC_API_URL=https://your-backend-domain.com \
     chatbot-frontend
   ```

## ☁️ Cloud Deployment Options

### Option 1: Heroku

#### Backend Deployment
1. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   ```

2. **Create Heroku app**
   ```bash
   cd Backend
   heroku create your-chatbot-api
   ```

3. **Set environment variables**
   ```bash
   heroku config:set OPENAI_API_KEY=your_key_here
   heroku config:set CORS_ORIGINS=https://your-frontend-domain.com
   ```

4. **Deploy**
   ```bash
   git subtree push --prefix Backend heroku main
   ```

#### Frontend Deployment (Vercel)
1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd Frontend
   vercel --prod
   ```

3. **Set environment variables in Vercel dashboard**
   - `NEXT_PUBLIC_API_URL=https://your-chatbot-api.herokuapp.com`

### Option 2: AWS ECS with Fargate

#### Prerequisites
- AWS CLI configured
- ECR repositories created
- ECS cluster setup

#### Backend Deployment
1. **Build and push to ECR**
   ```bash
   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and tag
   docker build -t chatbot-backend ./Backend
   docker tag chatbot-backend:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest
   
   # Push
   docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest
   ```

2. **Create ECS task definition**
   ```json
   {
     "family": "chatbot-backend",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "chatbot-backend",
         "image": "<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "OPENAI_API_KEY",
             "value": "your_key_here"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/chatbot-backend",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

#### Frontend Deployment (Vercel/Netlify)
Deploy frontend to Vercel or Netlify with:
- `NEXT_PUBLIC_API_URL=https://your-alb-url.com`

### Option 3: Google Cloud Run

#### Backend Deployment
1. **Enable Cloud Run API**
   ```bash
   gcloud services enable run.googleapis.com
   ```

2. **Build and deploy**
   ```bash
   cd Backend
   gcloud run deploy chatbot-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your_key_here
   ```

#### Frontend Deployment
Deploy to Vercel/Netlify with the Cloud Run URL.

### Option 4: DigitalOcean App Platform

1. **Create app spec**
   ```yaml
   # app.yaml
   name: chatbot-app
   services:
   - name: backend
     source_dir: Backend
     github:
       repo: your-username/chatbot
       branch: main
     run_command: uvicorn app:app --host 0.0.0.0 --port 8000
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: OPENAI_API_KEY
       value: your_key_here
     - key: CORS_ORIGINS
       value: https://your-frontend-domain.com
   - name: frontend
     source_dir: Frontend
     github:
       repo: your-username/chatbot
       branch: main
     run_command: npm start
     environment_slug: node-js
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: NEXT_PUBLIC_API_URL
       value: https://your-backend-domain.com
   ```

2. **Deploy**
   ```bash
   doctl apps create --spec app.yaml
   ```

## 🔐 Security Considerations

### Environment Variables
- Never commit API keys to version control
- Use environment-specific configurations
- Rotate API keys regularly

### CORS Configuration
- Set specific origins instead of "*"
- Use HTTPS in production
- Implement rate limiting

### Container Security
- Use non-root users in containers
- Scan images for vulnerabilities
- Keep base images updated

## 📊 Monitoring & Logging

### Health Checks
- `/health` endpoint for backend monitoring
- Set up uptime monitoring (Pingdom, UptimeRobot)

### Logging
- Centralized logging with ELK stack or similar
- Log aggregation in cloud platforms
- Error tracking with Sentry

### Performance Monitoring
- Application performance monitoring (APM)
- Database query monitoring
- API response time tracking

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "your-chatbot-api"
        heroku_email: "your-email@example.com"
        appdir: "Backend"

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-args: '--prod'
        working-directory: './Frontend'
```

## 🧪 Testing in Production

### Smoke Tests
- Basic functionality testing
- API endpoint availability
- Image upload functionality

### Load Testing
- Use tools like Artillery, JMeter
- Test concurrent user scenarios
- Monitor resource usage

## 📈 Scaling Considerations

### Backend Scaling
- Horizontal scaling with load balancers
- Auto-scaling based on CPU/memory
- Database connection pooling

### Frontend Scaling
- CDN for static assets
- Image optimization
- Caching strategies

## 🚨 Troubleshooting

### Common Issues
1. **OpenAI API Rate Limits**
   - Implement retry logic
   - Use exponential backoff
   - Monitor usage quotas

2. **CORS Errors**
   - Verify CORS_ORIGINS configuration
   - Check frontend API URL

3. **File Upload Issues**
   - Verify file size limits
   - Check supported file types
   - Monitor disk space

### Debugging Steps
1. Check application logs
2. Verify environment variables
3. Test API endpoints directly
4. Monitor resource usage
5. Check network connectivity

## 📞 Support

For deployment issues:
1. Check logs for error messages
2. Verify all environment variables
3. Test locally first
4. Check cloud provider status pages

---

**Happy deploying! 🎉** 