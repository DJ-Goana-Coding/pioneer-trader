# 🔗 REPOSITORY CONNECTIONS GUIDE

**Last Updated:** 2026-04-04
**Status:** ✅ CONNECTIONS ESTABLISHED

---

## 📊 CONNECTED REPOSITORIES

### 1. Pioneer Trader (Current Repository)
- **GitHub URL:** https://github.com/DJ-Goana-Coding/pioneer-trader
- **Purpose:** Trading execution engine, VortexBerserker V3.1.0
- **Branch:** `claude/connect-mapping-inventory-repo`
- **Components:**
  - Backend trading system
  - FastAPI endpoints
  - Frontend UI stencil pack
  - VortexBerserker fleet management (2/4/1 configuration)

### 2. Mapping and Inventory
- **GitHub URL:** https://github.com/DJ-Goana-Coding/mapping-and-inventory
- **Purpose:** Airgap bridge, Google Drive sync, fleet manifest management
- **Status:** ✅ CLONED AND CONNECTED
- **Location:** `/home/runner/work/pioneer-trader/pioneer-trader/mapping-and-inventory/`
- **Key Components:**
  - Fleet inventory reports
  - System documentation
  - Bridge protocols
  - Character activation systems

### 3. Hugging Face Space
- **Platform:** Hugging Face Spaces
- **Intended URL:** https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader
- **Status:** ⏳ CONFIGURED (requires HF_TOKEN to deploy)
- **Deployment Method:** GitHub Actions workflow (`.github/workflows/sync_to_hf.yml`)

---

## 🛠️ CONNECTION SCRIPTS

### Connect to Mapping-and-Inventory
```bash
# Script location
/home/runner/work/pioneer-trader/pioneer-trader/scripts/connect_mapping_inventory.sh

# What it does:
# - Checks if mapping-and-inventory exists
# - Clones from GitHub if needed
# - Establishes connection for bridge protocol
```

### Push to Hugging Face
```bash
# Script location
/home/runner/work/pioneer-trader/pioneer-trader/scripts/push_to_huggingface.sh

# Prerequisites:
# - HF_TOKEN environment variable must be set
# - Hugging Face Space must be created

# Usage:
export HF_TOKEN='your_hugging_face_token_here'
./scripts/push_to_huggingface.sh
```

---

## 🔐 REQUIRED SECRETS

### GitHub Actions Secrets
To enable automatic sync to Hugging Face, add these secrets in GitHub:

1. **HF_TOKEN**
   - Get from: https://huggingface.co/settings/tokens
   - Required for: Automatic deployment to Hugging Face Spaces
   - Scope: Write access to Spaces

---

## 📋 THE TRINITY ARCHITECTURE

As documented in `SESSION_28_COMPLETE.md`, the system operates across three sovereign components:

### 1. pioneer-trader (This Repository)
- Execution Engine
- Frankfurt Node
- VortexBerserker V3.1.0
- 10-Slot Fleet Management
- FastAPI backend
- UI Stencil Pack

### 2. mapping-and-inventory
- Airgap Bridge
- Google Drive Sync Protocol
- Fleet Manifest Management
- System documentation hub
- Character activation systems
- Omnidimensional research

### 3. perimeter-scout (Mentioned but not connected)
- Security Aegis
- IP Auto-Ban System
- Intrusion Detection

---

## 🚀 DEPLOYMENT STATUS

| Target | Status | URL |
|--------|--------|-----|
| GitHub (pioneer-trader) | ✅ ACTIVE | https://github.com/DJ-Goana-Coding/pioneer-trader |
| GitHub (mapping-and-inventory) | ✅ CONNECTED | https://github.com/DJ-Goana-Coding/mapping-and-inventory |
| Hugging Face Space | ⏳ READY | https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader |
| Render | ⏳ CONFIGURED | Configured via render.yaml |

---

## 📖 HOW TO DEPLOY TO HUGGING FACE

### Method 1: Using GitHub Actions (Automatic)
1. Go to GitHub repository settings
2. Navigate to Secrets and Variables > Actions
3. Add secret: `HF_TOKEN` with your Hugging Face token
4. Push to `main` branch
5. GitHub Actions will automatically sync to Hugging Face

### Method 2: Manual Push (Using Script)
```bash
# 1. Set your HF_TOKEN
export HF_TOKEN='hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 2. Run the push script
./scripts/push_to_huggingface.sh

# 3. Verify deployment
# Visit: https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader
```

### Method 3: Direct Git Push
```bash
# 1. Add Hugging Face remote
git remote add hf https://DJ-Goana-Coding:$HF_TOKEN@huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader

# 2. Push to Hugging Face
git push hf main --force-with-lease
```

---

## ⚙️ CONFIGURATION FILES

### Hugging Face Deployment
- **Dockerfile:** Containerized deployment configuration
- **requirements.txt:** Python dependencies
- **start.sh:** Application startup script (port 7860)
- **README.md:** Contains Hugging Face metadata

### GitHub Actions
- **`.github/workflows/sync_to_hf.yml`:** Auto-sync to Hugging Face on push
- **`.github/workflows/codex_sync.yml`:** Additional sync workflow

---

## 🔄 SYNC PROTOCOLS

### Fleet Manifest Sync
- **Location:** Google Drive `CITADEL-BOT/fleet_manifest.json`
- **Update Frequency:** Every 30 seconds
- **Purpose:** Real-time trading parameter updates without code deployment

### Repository Sync
- **Trigger:** Push to main branch
- **Target:** Hugging Face Space
- **Method:** GitHub Actions workflow

---

## 📝 IMPORTANT NOTES

### The "Airgap" Rule
> Never hard-code variables. All trading thresholds, stakes, and parameters live in `fleet_manifest.json` on Google Drive.

### The "Trinity" Dependency
> Changes to `VortexBerserker` in `pioneer-trader` must be coordinated with `bridge_protocol.py` in `mapping-and-inventory`.

### Security
- Never commit API keys or tokens
- Use GitHub Secrets for sensitive data
- Hugging Face Space can be set to Private for sensitive data

---

## 🎯 NEXT STEPS

1. [ ] Set HF_TOKEN as GitHub secret
2. [ ] Create Hugging Face Space if not exists
3. [ ] Merge this branch to main to trigger auto-deployment
4. [ ] Verify deployment on Hugging Face
5. [ ] Update DEPLOYMENT_STATUS.md with live URLs

---

## 📞 TROUBLESHOOTING

### Connection Failed
- Check network connectivity
- Verify repository URLs
- Ensure proper permissions

### Hugging Face Push Fails
- Verify HF_TOKEN is valid
- Check Space exists on Hugging Face
- Ensure write permissions

### Mapping-and-Inventory Not Found
- Run `./scripts/connect_mapping_inventory.sh`
- Verify GitHub access permissions
- Check repository visibility

---

*This document establishes the Trinity Architecture connection protocol for the Pioneer Trader ecosystem.*
