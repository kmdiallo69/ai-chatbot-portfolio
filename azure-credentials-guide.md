# Azure Credentials Setup for Learning Environment

## 🔐 **GitHub Secrets to Add**

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

### 1. **AZURE_STATIC_WEB_APPS_API_TOKEN_BLUE_GRASS_012BC941E**
**Secret Name**: `AZURE_STATIC_WEB_APPS_API_TOKEN_BLUE_GRASS_012BC941E`
**Secret Value**: `8a84f17a67ccacfca21994b134a8fcc8dcdf4a95e9fdbc29ec37cd9cddb4c3f702-89b1b967-e7b8-4da8-8823-3f1e2ee0dbe701e0215012bc941e`

### 2. **OPENAI_API_KEY**
**Secret Name**: `OPENAI_API_KEY`
**Secret Value**: Use the key from your `Backend/config.env` file (starts with `sk-proj-...`)

## 📋 **Step-by-Step Setup**

1. **Go to GitHub**: https://github.com/kind-Kindi/Chatbot
2. **Click**: Settings → Secrets and variables → Actions
3. **Add each secret** with the exact names and values above
4. **Commit and push** to trigger deployment

## 🚀 **Deploy Frontend**

Once you add the secrets, you can deploy the frontend by pushing to GitHub or manually triggering the workflow.

## 🔧 **Backend Fix**

The backend is running but needs database connection fixed. We'll handle this after the frontend deployment.

## 🎯 **Your Application URLs**

- **Frontend**: https://blue-grass-012bc941e.2.azurestaticapps.net
- **Backend**: https://chatbot-backend.kindwater-a13bf119.westus.azurecontainerapps.io
- **Database**: https://chatbot-database.kindwater-a13bf119.westus.azurecontainerapps.io

## 🌐 **Azure Resources Created**

- **Resource Group**: `1-410dbcf4-playground-sandbox`
- **Container Registry**: `chatbotacr1752346001`
- **Container Apps Environment**: `chatbot-env-1752346023`
- **Static Web App**: `chatbot-frontend-1752346284`

## 🚀 **Ready to Deploy**

Once you add the GitHub secrets, your frontend will deploy automatically! 