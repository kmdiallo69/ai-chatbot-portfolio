# Azure Deployment Guide 🌐

Deploy your AI Chatbot to Azure and make it publicly accessible.

## 🏗️ **Architecture Overview**

```
Internet → Azure Static Web Apps (Frontend) → Azure Container Apps (Backend) → OpenAI API
```

## 📋 **Prerequisites**

1. **Azure Account**
   - Active Azure subscription
   - Resource group created

2. **Tools Installation**
   ```bash
   # Install Azure CLI
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Login to Azure
   az login
   
   # Install Docker Desktop
   # Download from: https://www.docker.com/products/docker-desktop
   ```

3. **Environment Setup**
   - OpenAI API key
   - GitHub repository with your code

## 🚀 **Method 1: Container Apps + Static Web Apps**

### **Step 1: Deploy Backend to Azure Container Apps**

1. **Create Resource Group**
   ```bash
   az group create --name chatbot-rg --location eastus
   ```

2. **Create Container Apps Environment**
   ```bash
   az containerapp env create \
     --name chatbot-env \
     --resource-group chatbot-rg \
     --location eastus
   ```

3. **Build and Deploy Backend**
   ```bash
   # Navigate to project root
   cd /path/to/your/Chatbot
   
   # Build and push to Azure Container Registry
   az acr create --resource-group chatbot-rg --name chatbotacr --sku Basic
   az acr login --name chatbotacr
   
   # Build and push backend image
   docker build -t chatbotacr.azurecr.io/chatbot-backend:latest ./Backend
   docker push chatbotacr.azurecr.io/chatbot-backend:latest
   
   # Deploy to Container Apps
   az containerapp create \
     --name chatbot-backend \
     --resource-group chatbot-rg \
     --environment chatbot-env \
     --image chatbotacr.azurecr.io/chatbot-backend:latest \
     --target-port 8000 \
     --ingress external \
     --registry-server chatbotacr.azurecr.io \
     --env-vars OPENAI_API_KEY=your_openai_key_here \
     --min-replicas 1 \
     --max-replicas 3
   ```

4. **Get Backend URL**
   ```bash
   az containerapp show \
     --name chatbot-backend \
     --resource-group chatbot-rg \
     --query "properties.configuration.ingress.fqdn" \
     --output tsv
   ```

### **Step 2: Deploy Frontend to Azure Static Web Apps**

1. **Create Static Web App**
   ```bash
   az staticwebapp create \
     --name chatbot-frontend \
     --resource-group chatbot-rg \
     --source https://github.com/YOUR_USERNAME/YOUR_REPO \
     --branch main \
     --app-location "/Frontend" \
     --api-location "" \
     --output-location ".next" \
     --login-with-github
   ```

2. **Configure Environment Variables**
   ```bash
   # Get the backend URL from step 1
   BACKEND_URL="https://your-backend-url.azurecontainerapps.io"
   
   # Set environment variable
   az staticwebapp appsettings set \
     --name chatbot-frontend \
     --resource-group chatbot-rg \
     --setting-names NEXT_PUBLIC_API_URL=$BACKEND_URL
   ```

### **Step 3: Configure GitHub Actions (Auto-generated)**

The Static Web App will automatically create a GitHub Actions workflow. Update the workflow file:

```yaml
# .github/workflows/azure-static-web-apps-xxx.yml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches:
      - main
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches:
      - main

jobs:
  build_and_deploy_job:
    if: github.event_name == 'push' || (github.event_name == 'pull_request' && github.event.action != 'closed')
    runs-on: ubuntu-latest
    name: Build and Deploy Job
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true
      - name: Build And Deploy
        id: builddeploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/Frontend"
          api_location: ""
          output_location: ".next"
        env:
          NEXT_PUBLIC_API_URL: https://your-backend-url.azurecontainerapps.io
```

## 🚀 **Method 2: App Service (Alternative)**

### **Backend Deployment**

1. **Create App Service Plan**
   ```bash
   az appservice plan create \
     --name chatbot-plan \
     --resource-group chatbot-rg \
     --is-linux \
     --sku B1
   ```

2. **Deploy Backend**
   ```bash
   az webapp create \
     --name chatbot-backend-app \
     --resource-group chatbot-rg \
     --plan chatbot-plan \
     --deployment-container-image-name chatbotacr.azurecr.io/chatbot-backend:latest
   
   # Configure environment variables
   az webapp config appsettings set \
     --name chatbot-backend-app \
     --resource-group chatbot-rg \
     --settings OPENAI_API_KEY=your_openai_key_here
   ```

### **Frontend Deployment**

1. **Create Frontend App Service**
   ```bash
   az webapp create \
     --name chatbot-frontend-app \
     --resource-group chatbot-rg \
     --plan chatbot-plan \
     --deployment-container-image-name chatbotacr.azurecr.io/chatbot-frontend:latest
   
   # Configure environment variables
   az webapp config appsettings set \
     --name chatbot-frontend-app \
     --resource-group chatbot-rg \
     --settings NEXT_PUBLIC_API_URL=https://chatbot-backend-app.azurewebsites.net
   ```

## 🔧 **Configuration Files for Azure**

### **Backend Configuration for Azure**

Create `Backend/azure-startup.sh`:
```bash
#!/bin/bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Update `Backend/Dockerfile` for Azure:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script
COPY azure-startup.sh /app/
RUN chmod +x /app/azure-startup.sh

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["/app/azure-startup.sh"]
```

### **Frontend Configuration for Azure**

Update `Frontend/next.config.mjs`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  trailingSlash: true,
  experimental: {
    outputFileTracingRoot: undefined,
  },
  // Azure Static Web Apps configuration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;
```

## 🌐 **Custom Domain Setup (Optional)**

### **For Static Web Apps**
1. **Add Custom Domain**
   ```bash
   az staticwebapp hostname set \
     --name chatbot-frontend \
     --resource-group chatbot-rg \
     --hostname your-domain.com
   ```

2. **Configure DNS**
   - Add CNAME record pointing to your Static Web App URL
   - Azure will automatically provision SSL certificate

### **For Container Apps**
1. **Add Custom Domain**
   ```bash
   az containerapp hostname add \
     --name chatbot-backend \
     --resource-group chatbot-rg \
     --hostname api.your-domain.com
   ```

## 🔐 **Security Configuration**

### **Backend Security**
```bash
# Update CORS settings
az containerapp update \
  --name chatbot-backend \
  --resource-group chatbot-rg \
  --set-env-vars CORS_ORIGINS=https://your-frontend-domain.com
```

### **Frontend Security**
- Static Web Apps automatically provides HTTPS
- Configure Content Security Policy in next.config.mjs

## 📊 **Monitoring & Logging**

### **Application Insights**
```bash
# Create Application Insights
az monitor app-insights component create \
  --app chatbot-insights \
  --location eastus \
  --resource-group chatbot-rg
```

### **Log Analytics**
```bash
# Enable logging for Container Apps
az containerapp logs show \
  --name chatbot-backend \
  --resource-group chatbot-rg \
  --follow
```

## 💰 **Cost Optimization**

### **Resource Sizing**
- **Container Apps**: Start with 0.25 CPU, 0.5Gi memory
- **Static Web Apps**: Free tier available
- **Container Registry**: Basic tier for small projects

### **Auto-scaling**
```bash
# Configure auto-scaling rules
az containerapp update \
  --name chatbot-backend \
  --resource-group chatbot-rg \
  --min-replicas 0 \
  --max-replicas 5
```

## 🚀 **Deployment Steps Summary**

### **Quick Deployment Checklist**
1. ✅ Create Azure Resource Group
2. ✅ Set up Container Registry
3. ✅ Build and push Docker images
4. ✅ Deploy backend to Container Apps
5. ✅ Deploy frontend to Static Web Apps
6. ✅ Configure environment variables
7. ✅ Set up custom domain (optional)
8. ✅ Configure monitoring
9. ✅ Test the application

### **Expected URLs**
- **Frontend**: `https://your-app-name.azurestaticapps.net`
- **Backend**: `https://your-backend.azurecontainerapps.io`

## 🧪 **Testing Deployment**

### **Health Checks**
```bash
# Test backend health
curl https://your-backend.azurecontainerapps.io/health

# Test frontend
curl https://your-app-name.azurestaticapps.net
```

### **Load Testing**
```bash
# Install Artillery
npm install -g artillery

# Test API endpoints
artillery quick --count 10 --num 5 https://your-backend.azurecontainerapps.io/health
```

## 🚨 **Troubleshooting**

### **Common Issues**
1. **Container startup failures**: Check logs with `az containerapp logs`
2. **CORS errors**: Verify CORS_ORIGINS environment variable
3. **API connection issues**: Check frontend API URL configuration

### **Debug Commands**
```bash
# Check container app status
az containerapp show --name chatbot-backend --resource-group chatbot-rg

# View logs
az containerapp logs show --name chatbot-backend --resource-group chatbot-rg --follow

# Check static web app
az staticwebapp show --name chatbot-frontend --resource-group chatbot-rg
```

## 📱 **Mobile Optimization**

Your responsive design will work perfectly on mobile devices through Azure's global CDN.

## 🎯 **Next Steps**

1. **Monitor Performance**: Set up Application Insights
2. **Scale Based on Usage**: Configure auto-scaling rules
3. **Add Authentication**: Implement Azure AD B2C
4. **Database Integration**: Add Azure Cosmos DB for chat history
5. **CI/CD Pipeline**: Set up automated deployments

---

**Your chatbot will be live on the internet with global availability! 🌍** 