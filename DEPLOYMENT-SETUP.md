# 🚀 Deployment Setup Guide

## ✅ **What's Already Done**

I've updated your project with the following Azure resources:
- **Resource Group**: `1-410dbcf4-playground-sandbox`
- **Container Registry**: `chatbotacr1752346001`
- **Container Apps Environment**: `chatbot-env-1752346023`
- **Static Web App**: `chatbot-frontend-1752346284`
- **Frontend URL**: `https://blue-grass-012bc941e.2.azurestaticapps.net`
- **Location**: `westus`

## 🔐 **GitHub Secrets Required**

You need to set up these secrets in your GitHub repository:

### 1. **AZURE_CREDENTIALS**
Since you can't create a service principal with your current permissions, you have two options:

#### Option A: Use Azure CLI Credentials (Temporary)
```bash
# Get your current Azure account info
az account show --output json
```

Create a JSON in this format:
```json
{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret",
  "subscriptionId": "9734ed68-621d-47ed-babd-269110dbacb1",
  "tenantId": "your-tenant-id"
}
```

#### Option B: Contact Administrator
Ask your Azure administrator to create a service principal with these permissions:
- **Role**: Contributor
- **Scope**: `/subscriptions/9734ed68-621d-47ed-babd-269110dbacb1/resourceGroups/1-410dbcf4-playground-sandbox`

### 2. **AZURE_STATIC_WEB_APPS_API_TOKEN_BLUE_GRASS_012BC941E**
Value: `8a84f17a67ccacfca21994b134a8fcc8dcdf4a95e9fdbc29ec37cd9cddb4c3f702-89b1b967-e7b8-4da8-8823-3f1e2ee0dbe701e0215012bc941e`

### 3. **OPENAI_API_KEY**
Get your OpenAI API key from: https://platform.openai.com/api-keys
Format: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 📋 **How to Set GitHub Secrets**

1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name and value above

## 🔧 **Manual Azure Authentication Setup**

If you have owner permissions on the subscription, try this:

```bash
# Create service principal (requires higher permissions)
az ad sp create-for-rbac \
  --name "GitHubActions-Chatbot" \
  --role contributor \
  --scopes /subscriptions/9734ed68-621d-47ed-babd-269110dbacb1 \
  --json-auth

# Or create with resource group scope
az ad sp create-for-rbac \
  --name "GitHubActions-Chatbot" \
  --role contributor \
  --scopes /subscriptions/9734ed68-621d-47ed-babd-269110dbacb1/resourceGroups/1-410dbcf4-playground-sandbox \
  --json-auth
```

## 🚀 **Deploy Your Application**

Once you have set up all the GitHub secrets:

1. **Commit and push your changes**:
   ```bash
   git add .
   git commit -m "Update Azure deployment configuration"
   git push origin main
   ```

2. **GitHub Actions will automatically**:
   - Build and deploy your database
   - Build and deploy your backend
   - Build and deploy your frontend
   - Configure all connections

## 🔍 **Verify Deployment**

After deployment, check:
- **Frontend**: https://blue-grass-012bc941e.2.azurestaticapps.net
- **Backend**: Will be displayed in GitHub Actions logs
- **Database**: Will be connected automatically

## 🧪 **Test Your Application**

1. Visit the frontend URL
2. Register a new user account
3. Test the chat functionality
4. Upload images and test AI responses

## 📊 **Monitor Your Deployment**

```bash
# Check backend logs
az containerapp logs show \
  --name chatbot-backend \
  --resource-group 1-410dbcf4-playground-sandbox \
  --follow

# Check database logs
az containerapp logs show \
  --name chatbot-database \
  --resource-group 1-410dbcf4-playground-sandbox \
  --follow
```

## 🐛 **Troubleshooting**

### Common Issues:
1. **Authentication Failed**: Check AZURE_CREDENTIALS secret
2. **OpenAI API Error**: Verify OPENAI_API_KEY secret
3. **Static Web App Deploy Failed**: Check AZURE_STATIC_WEB_APPS_API_TOKEN
4. **Database Connection Error**: Check container logs

### Get Help:
- View GitHub Actions logs for detailed error messages
- Check Azure portal for resource status
- Use Azure CLI to debug individual components

## 🏗️ **Architecture Overview**

```
Internet → Static Web App (Frontend) → Container App (Backend) → Container App (Database)
                                    ↓
                                OpenAI API
```

## 💰 **Cost Estimation**

With your current setup:
- **Static Web App**: FREE (100GB bandwidth/month)
- **Container Apps**: FREE (180,000 vCPU-seconds/month)
- **Container Registry**: FREE (1 repository)
- **Estimated Monthly Cost**: $0-5 for light usage

## 🎯 **Next Steps**

1. Set up GitHub secrets
2. Push changes to trigger deployment
3. Test your application
4. Configure custom domain (optional)
5. Set up monitoring and alerts

---

🚀 **Your chatbot will be live on the internet once the secrets are configured!** 