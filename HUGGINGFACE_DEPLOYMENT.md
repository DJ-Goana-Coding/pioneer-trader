# 🚀 HUGGING FACE DEPLOYMENT GUIDE

**Repository:** Pioneer Trader V2 Monolith  
**Last Updated:** 2026-01-25

---

## ✅ CURRENT STATUS

### Repository Configuration: READY ✅

All required configuration files for Hugging Face Spaces deployment are in place:

1. **README.md** - Contains Hugging Face metadata (lines 1-8)
2. **Dockerfile** - Container configuration for deployment
3. **requirements.txt** - Python dependencies
4. **start.sh** - Application startup script (configured for port 7860)

### Deployment Status: NOT YET DEPLOYED ⏳

The repository is **fully configured** but has **not yet been deployed** to Hugging Face Spaces.

---

## 📋 DEPLOYMENT STEPS

### Option 1: Deploy via GitHub Integration (Recommended)

1. **Create Hugging Face Account**
   - Visit: https://huggingface.co/join
   - Sign up or log in

2. **Create a New Space**
   - Go to: https://huggingface.co/new-space
   - Fill in the form:
     - **Owner:** Your username/organization
     - **Space name:** `pioneer-trader`
     - **License:** Choose appropriate license (e.g., Apache 2.0)
     - **SDK:** Select `Docker`
     - **Visibility:** Public or Private

3. **Link GitHub Repository**
   - In Space settings, find "Repository" section
   - Click "Link a GitHub repository"
   - Authorize Hugging Face to access GitHub
   - Select: `DJ-Goana-Coding/pioneer-trader`
   - Choose branch: `main`

4. **Configure Build Settings**
   - Hugging Face will automatically detect the `Dockerfile`
   - No additional configuration needed
   - The app will run on port 7860 (already configured)

5. **Deploy**
   - Click "Deploy" or commit to trigger build
   - Wait for build to complete (typically 5-10 minutes)
   - Your app will be available at: `https://huggingface.co/spaces/[username]/pioneer-trader`

### Option 2: Deploy via Git Push

1. **Create Space on Hugging Face** (same as Option 1, steps 1-2)

2. **Clone the Space Repository**
   ```bash
   git clone https://huggingface.co/spaces/[username]/pioneer-trader
   cd pioneer-trader
   ```

3. **Add GitHub Remote and Pull**
   ```bash
   git remote add github https://github.com/DJ-Goana-Coding/pioneer-trader.git
   git pull github main
   ```

4. **Push to Hugging Face**
   ```bash
   git push origin main
   ```

5. **Automatic Deployment**
   - Hugging Face will detect changes and rebuild
   - App will be live at: `https://huggingface.co/spaces/[username]/pioneer-trader`

---

## 🔧 CONFIGURATION DETAILS

### README.md Metadata
```yaml
---
title: Pioneer Trader
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
```

This metadata tells Hugging Face:
- **title:** Display name of the Space
- **emoji:** Icon shown in the Space
- **colorFrom/colorTo:** Gradient colors for the Space banner
- **sdk:** Use Docker runtime
- **app_port:** Application listens on port 7860

### Dockerfile Configuration
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x start.sh
CMD ["./start.sh"]
```

### Start Script (start.sh)
```bash
#!/bin/bash
export PORT=${PORT:-7860}
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

---

## ⚠️ IMPORTANT NOTES

### Environment Variables
The application requires these environment variables:
- `BINANCE_API_KEY` - Your Binance API key
- `BINANCE_SECRET` - Your Binance secret key
- `PORT` - Application port (defaults to 7860)

**To add secrets on Hugging Face:**
1. Go to your Space settings
2. Navigate to "Repository secrets"
3. Add each secret with its value
4. Redeploy the Space

### Security Considerations
- **Never commit API keys** to the repository
- Use Hugging Face Secrets for sensitive data
- Consider setting Space to "Private" if handling real trading data

### Resource Limits
- Free tier has limited compute resources
- For production trading, consider:
  - Upgrading to a paid tier
  - Using Render for main deployment (as documented)
  - Using Hugging Face as backup only

---

## 🔍 VERIFICATION

After deployment, verify the app is working:

1. **Check Space URL**
   - Visit: `https://huggingface.co/spaces/[username]/pioneer-trader`
   
2. **Check Logs**
   - Click "Logs" tab in your Space
   - Look for: "🛰️ T.I.A. COMMAND: IGNITING VORTEX ENGINE..."
   - Verify uvicorn starts on port 7860

3. **Test API**
   - Access: `https://[username]-pioneer-trader.hf.space/docs`
   - Should see FastAPI documentation

4. **Check Health**
   - Access: `https://[username]-pioneer-trader.hf.space/health` (if endpoint exists)

---

## 📞 TROUBLESHOOTING

### Build Fails
- Check "Logs" tab for error messages
- Verify all dependencies in requirements.txt are available
- Ensure Dockerfile syntax is correct

### App Not Accessible
- Verify port 7860 is exposed
- Check start.sh is executable
- Review application logs for startup errors

### API Keys Not Working
- Verify secrets are added in Space settings
- Check secret names match code expectations
- Redeploy after adding secrets

---

## 📊 DEPLOYMENT MATRIX

| Platform | Status | Purpose | URL |
|----------|--------|---------|-----|
| GitHub | ✅ ACTIVE | Source Code | https://github.com/DJ-Goana-Coding/pioneer-trader |
| Hugging Face | ⏳ READY | Backup/Demo | To be deployed |
| Render | ⏳ READY | Production | Configured via render.yaml |

---

## 🎯 NEXT STEPS

To complete Hugging Face deployment:

1. [ ] Create Hugging Face account (if needed)
2. [ ] Create new Space named "pioneer-trader"
3. [ ] Link to GitHub repository OR push code directly
4. [ ] Add required environment variables as Secrets
5. [ ] Wait for build to complete
6. [ ] Verify deployment and update DEPLOYMENT_STATUS.md with URL
7. [ ] Test all endpoints and functionality

---

*This guide ensures Pioneer Trader V2 can be deployed to Hugging Face Spaces as a redundant backup to the main Render deployment.*
