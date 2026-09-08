# 🚀 QUICKSTART: Repository Connections & HuggingFace Deployment

**For:** Commander Darrell
**Purpose:** Quick reference to connect repositories and deploy to Hugging Face
**Last Updated:** 2026-04-04

---

## ⚡ IMMEDIATE ACTIONS

### 1. Connect to mapping-and-inventory Repository
```bash
cd /path/to/pioneer-trader
./scripts/connect_mapping_inventory.sh
```

**What This Does:**
- ✅ Checks if mapping-and-inventory repository exists
- ✅ Clones it from GitHub if needed: `https://github.com/DJ-Goana-Coding/mapping-and-inventory`
- ✅ Creates local connection for Trinity Architecture

**Result:**
- Directory: `./mapping-and-inventory/` (git-ignored in pioneer-trader)
- Status: Full separate repository ready for independent work

---

### 2. Push to Hugging Face

#### Option A: Using the Script (Recommended)
```bash
# 1. Get your Hugging Face token
# Visit: https://huggingface.co/settings/tokens
# Click "New token" → Select "Write" access → Copy token

# 2. Set token as environment variable
export HF_TOKEN='hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 3. Run the push script
./scripts/push_to_huggingface.sh
```

#### Option B: Using GitHub Actions (Automatic)
```bash
# 1. Add HF_TOKEN as GitHub Secret
# Go to: https://github.com/DJ-Goana-Coding/pioneer-trader/settings/secrets/actions
# Click "New repository secret"
# Name: HF_TOKEN
# Value: your_huggingface_token

# 2. Merge to main branch
git checkout main
git merge claude/connect-mapping-inventory-repo
git push origin main

# 3. GitHub Actions will automatically push to HuggingFace
# Watch: https://github.com/DJ-Goana-Coding/pioneer-trader/actions
```

---

## 📋 PREREQUISITES

### Before Pushing to Hugging Face
1. **Create Hugging Face Account** (if not already done)
   - URL: https://huggingface.co/join

2. **Create Hugging Face Space** (if not already created)
   - URL: https://huggingface.co/new-space
   - Name: `pioneer-trader`
   - SDK: Select `Docker`
   - Visibility: Public or Private

3. **Get HF_TOKEN**
   - URL: https://huggingface.co/settings/tokens
   - Create token with "Write" access

---

## 🔍 VERIFY DEPLOYMENT

### Check Hugging Face Space
```bash
# Your app will be available at:
https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader

# API Documentation:
https://DJ-Goana-Coding-pioneer-trader.hf.space/docs

# Health Check:
curl https://DJ-Goana-Coding-pioneer-trader.hf.space/health
```

Expected response:
```json
{
  "status": "ok",
  "Safety Locks": "ENGAGED ✅"
}
```

---

## 🛠️ TROUBLESHOOTING

### "HF_TOKEN not set"
```bash
# Make sure you exported the token
export HF_TOKEN='your_token_here'

# Verify it's set
echo $HF_TOKEN
```

### "Connection failed"
```bash
# Check if Hugging Face Space exists
# Visit: https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader

# If not, create it first:
# https://huggingface.co/new-space
```

### "mapping-and-inventory not found"
```bash
# Check if repository exists on GitHub
git ls-remote https://github.com/DJ-Goana-Coding/mapping-and-inventory.git

# If yes, run the connection script
./scripts/connect_mapping_inventory.sh
```

---

## 📖 REFERENCE DOCUMENTS

| Document | Purpose |
|----------|---------|
| `REPOSITORY_CONNECTIONS.md` | Full connection guide and Trinity Architecture |
| `HUGGINGFACE_DEPLOYMENT.md` | Detailed HuggingFace deployment instructions |
| `SESSION_28_COMPLETE.md` | Trinity Architecture implementation details |
| `scripts/connect_mapping_inventory.sh` | Automated connection script |
| `scripts/push_to_huggingface.sh` | Automated HF push script |

---

## 🎯 THE TRINITY ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    TRINITY ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │  pioneer-trader  │  │ mapping-and-inv  │              │
│  │                  │◄─┤                  │              │
│  │  • VortexBerserker│ │  • Airgap Bridge │              │
│  │  • Trading Engine │  │  • Fleet Manifest│              │
│  │  • FastAPI Backend│  │  • Documentation │              │
│  └────────┬─────────┘  └──────────────────┘              │
│           │                                                │
│           ▼                                                │
│  ┌──────────────────┐                                     │
│  │  Hugging Face    │                                     │
│  │  Deployment      │                                     │
│  │  Port: 7860      │                                     │
│  └──────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ CONFIGURATION FILES

| File | Purpose |
|------|---------|
| `.github/workflows/sync_to_hf.yml` | Auto-sync to HuggingFace on main branch push |
| `Dockerfile` | Container configuration for HF deployment |
| `requirements.txt` | Python dependencies |
| `start.sh` | Startup script (port 7860 for HF) |
| `README.md` | HuggingFace metadata in front matter |

---

## 🎬 COMPLETE WORKFLOW

```bash
# 1. Connect to mapping-and-inventory
./scripts/connect_mapping_inventory.sh

# 2. Set HuggingFace token
export HF_TOKEN='hf_your_token_here'

# 3. Push to HuggingFace
./scripts/push_to_huggingface.sh

# 4. Verify deployment
curl https://DJ-Goana-Coding-pioneer-trader.hf.space/health

# Done! ✅
```

---

*For detailed information, see `REPOSITORY_CONNECTIONS.md`*
