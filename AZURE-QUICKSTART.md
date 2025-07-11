# Azure Deployment - Quick Start Guide 🚀

## What You Need (Requirements)

### 1. **Azure Account**
- Free Azure account: https://azure.microsoft.com/free/
- You get $200 credit for the first 30 days

### 2. **GitHub Repository**
- Push your chatbot code to GitHub
- Make sure it's public or give Azure access

### 3. **OpenAI API Key**
- Get it from: https://platform.openai.com/api-keys
- You need a valid OpenAI account with billing set up

### 4. **Tools Installation**
```bash
# Install Azure CLI (on Mac/Linux)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Or on Windows with PowerShell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop
```

## 🚀 **Simple 3-Step Deployment**

### **Step 1: Setup Environment Variables**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-openai-key-here"

# Set your GitHub repository URL
export GITHUB_REPO="https://github.com/yourusername/your-chatbot-repo"
```

### **Step 2: Login to Azure**
```bash
# Login to Azure
az login
# This will open a browser window - login with your Azure account
```

### **Step 3: Run the Deployment Script**
```bash
# Make the script executable
chmod +x azure-deploy.sh

# Run the deployment (this takes about 5-10 minutes)
./azure-deploy.sh
```

**That's it!** The script will:
- ✅ Create all Azure resources
- ✅ Build and deploy your backend
- ✅ Deploy your frontend
- ✅ Configure everything automatically
- ✅ Give you the final URLs

## 🌐 **Expected Results**

After deployment, you'll get:
- **Frontend URL**: `https://chatbot-frontend.azurestaticapps.net`
- **Backend URL**: `https://chatbot-backend.azurecontainerapps.io`

## 💰 **Cost Breakdown**

### **Free Tier Usage (For Portfolio)**
- **Static Web Apps**: FREE (100GB bandwidth/month)
- **Container Apps**: FREE (180,000 vCPU-seconds/month)
- **Container Registry**: FREE (1 repository)
- **Total Monthly Cost**: ~$0-5 for light usage

### **If You Exceed Free Tier**
- **Container Apps**: ~$0.000024/vCPU-second
- **Static Web Apps**: ~$0.20/GB bandwidth
- **Container Registry**: ~$5/month for Basic

## 🔧 **Manual Deployment (Alternative)**

If you prefer to do it step by step:

### **Backend Deployment**
```bash
# 1. Create resource group
az group create --name chatbot-rg --location eastus

# 2. Create container registry
az acr create --resource-group chatbot-rg --name chatbotacr --sku Basic
az acr login --name chatbotacr

# 3. Build and push backend
docker build -t chatbotacr.azurecr.io/chatbot-backend:latest -f Backend/Dockerfile.azure ./Backend
docker push chatbotacr.azurecr.io/chatbot-backend:latest

# 4. Create container apps environment
az containerapp env create --name chatbot-env --resource-group chatbot-rg --location eastus

# 5. Deploy backend
az containerapp create \
  --name chatbot-backend \
  --resource-group chatbot-rg \
  --environment chatbot-env \
  --image chatbotacr.azurecr.io/chatbot-backend:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server chatbotacr.azurecr.io \
  --env-vars OPENAI_API_KEY="$OPENAI_API_KEY" \
  --min-replicas 1 \
  --max-replicas 3
```

### **Frontend Deployment**
```bash
# 1. Deploy to Static Web Apps
az staticwebapp create \
  --name chatbot-frontend \
  --resource-group chatbot-rg \
  --source $GITHUB_REPO \
  --branch main \
  --app-location "/Frontend" \
  --api-location "" \
  --output-location ".next" \
  --login-with-github

# 2. Configure environment variables
BACKEND_URL=$(az containerapp show --name chatbot-backend --resource-group chatbot-rg --query "properties.configuration.ingress.fqdn" --output tsv)
az staticwebapp appsettings set \
  --name chatbot-frontend \
  --resource-group chatbot-rg \
  --setting-names NEXT_PUBLIC_API_URL="https://$BACKEND_URL"
```

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **"OpenAI API Key not set"**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

2. **"Docker not found"**
   - Install Docker Desktop and make sure it's running

3. **"az command not found"**
   - Install Azure CLI following the instructions above

4. **"Container registry login failed"**
   ```bash
   az acr login --name chatbotacr
   ```

5. **"GitHub authentication failed"**
   - Make sure you're logged into GitHub in your browser
   - Repository should be public or give Azure access

### **Checking Deployment Status**
```bash
# Check backend logs
az containerapp logs show --name chatbot-backend --resource-group chatbot-rg --follow

# Check frontend deployment
az staticwebapp show --name chatbot-frontend --resource-group chatbot-rg

# Test backend health
curl https://your-backend-url.azurecontainerapps.io/health
```

## 🎯 **After Deployment**

### **Test Your Application**
1. Visit your frontend URL
2. Try sending a text message
3. Upload an image and ask about it
4. Check that everything works

### **Monitor Your Application**
```bash
# View real-time logs
az containerapp logs show --name chatbot-backend --resource-group chatbot-rg --follow

# Check resource usage
az containerapp show --name chatbot-backend --resource-group chatbot-rg
```

### **Update Your Application**
```bash
# For backend updates
docker build -t chatbotacr.azurecr.io/chatbot-backend:latest -f Backend/Dockerfile.azure ./Backend
docker push chatbotacr.azurecr.io/chatbot-backend:latest
az containerapp update --name chatbot-backend --resource-group chatbot-rg --image chatbotacr.azurecr.io/chatbot-backend:latest

# For frontend updates - just push to GitHub, it auto-deploys!
```

## 🧹 **Cleanup (Delete Everything)**

When you're done testing:
```bash
# Delete the entire resource group (removes everything)
az group delete --name chatbot-rg --yes --no-wait
```

---

## 🎉 **Success!**

Once deployed, your chatbot will be:
- ✅ **Live on the internet** with global CDN
- ✅ **Automatically scaled** based on usage
- ✅ **Secured with HTTPS**
- ✅ **Ready for your portfolio**

Share the URL with employers to showcase your AI development skills! 🚀 