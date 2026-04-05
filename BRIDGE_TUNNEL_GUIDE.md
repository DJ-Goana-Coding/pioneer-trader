# 🌉 Bridge Tunnel: Mapping-and-Inventory → Hugging Face

This document describes the bridge/tunnel setup between the `mapping-and-inventory` GitHub repository and the Hugging Face Space `Mapping-and-Inventory`.

## 📋 Overview

The bridge tunnel automatically syncs content from the [DJ-Goana-Coding/mapping-and-inventory](https://github.com/DJ-Goana-Coding/mapping-and-inventory) repository to a Hugging Face Space where it's deployed as an interactive documentation browser.

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│  mapping-and-inventory Repo     │
│  (Source Documentation)          │
└──────────────┬──────────────────┘
               │
               │ Git Remote Connection
               │
               ▼
┌─────────────────────────────────┐
│  pioneer-trader Repo             │
│  (Bridge/Tunnel Scripts)         │
│  - sync script                   │
│  - GitHub Actions workflow       │
└──────────────┬──────────────────┘
               │
               │ Automated Sync
               │
               ▼
┌─────────────────────────────────┐
│  Hugging Face Space             │
│  Mapping-and-Inventory          │
│  (Interactive Documentation)     │
│  - Gradio Interface              │
│  - Docker Deployment             │
└─────────────────────────────────┘
```

## 🔧 Components

### 1. Git Remote Connection

The `mapping-and-inventory` repository has been added as a remote to `pioneer-trader`:

```bash
git remote add mapping-and-inventory https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
```

This allows us to:
- Fetch latest changes from mapping-and-inventory
- Track sync status
- Maintain connection between repos

### 2. Sync Script

**Location:** `scripts/sync_mapping_to_huggingface.sh`

This bash script:
- Fetches latest content from mapping-and-inventory
- Creates a temporary workspace
- Adds Hugging Face deployment files:
  - `README.md` with HF metadata
  - `Dockerfile` for Gradio app
  - `requirements.txt` for dependencies
  - `app.py` (generated) for documentation browser
- Provides instructions for manual deployment

**Usage:**
```bash
./scripts/sync_mapping_to_huggingface.sh
```

### 3. GitHub Actions Workflow

**Location:** `.github/workflows/sync-mapping-to-huggingface.yml`

Automates the sync process on:
- Manual trigger (workflow_dispatch)
- Daily schedule (midnight UTC)
- Push to main branch (when sync script changes)

**Steps:**
1. Clone mapping-and-inventory repository
2. Prepare Hugging Face deployment files
3. Deploy to Hugging Face Space (if HF_TOKEN is set)
4. Generate summary report

## 🚀 Deployment

### Initial Setup

#### 1. Create Hugging Face Space

1. Go to [https://huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in details:
   - **Name:** Mapping-and-Inventory
   - **SDK:** Docker
   - **Visibility:** Public or Private
3. Click "Create Space"

#### 2. Get Hugging Face Token

1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a new token with write permissions
3. Copy the token

#### 3. Add Token to GitHub Secrets

1. Go to repository settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `HF_TOKEN`
4. Value: [paste your HF token]
5. Click "Add secret"

### Manual Deployment

#### Option 1: Using the Sync Script

```bash
# Run the sync script
./scripts/sync_mapping_to_huggingface.sh

# Follow the instructions to push to Hugging Face
cd /tmp/mapping-and-inventory-hf-bridge

# Add Hugging Face remote
git remote add huggingface https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory

# Commit and push
git add -A
git commit -m "Deploy to Hugging Face Space"
git push huggingface main
```

#### Option 2: Using Hugging Face CLI

```bash
# Run the sync script first
./scripts/sync_mapping_to_huggingface.sh

# Install HF CLI
pip install huggingface-hub[cli]

# Login
huggingface-cli login

# Upload
cd /tmp/mapping-and-inventory-hf-bridge
huggingface-cli upload DJ-Goana-Coding/Mapping-and-Inventory . --repo-type=space
```

### Automated Deployment

Once the `HF_TOKEN` secret is set, the workflow will automatically:
- Sync daily at midnight UTC
- Deploy when manually triggered
- Update on script changes

**To manually trigger:**
1. Go to Actions tab in GitHub
2. Select "Bridge to Hugging Face - Mapping and Inventory"
3. Click "Run workflow"

## 📱 Accessing the Deployed Space

Once deployed, the Hugging Face Space will be available at:
[https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory](https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory)

### Features

The deployed space includes:
- **Interactive Documentation Browser:** Browse all markdown files
- **Search and Filter:** Find specific documentation quickly
- **File Tree View:** See the complete documentation structure
- **Gradio Interface:** User-friendly web UI
- **Quick Access Links:** Direct links to key documents

## 🔄 Sync Process

### What Gets Synced

All content from the mapping-and-inventory repository:
- Documentation files (*.md)
- Architecture diagrams
- Configuration files
- Scripts and tools
- All directories and subdirectories

### Sync Frequency

- **Automatic:** Daily at midnight UTC
- **Manual:** Trigger workflow anytime
- **On Changes:** When sync script is modified

## 🛠️ Maintenance

### Updating the Deployment

To update deployment files (Dockerfile, app.py, etc.):
1. Edit `.github/workflows/sync-mapping-to-huggingface.yml`
2. Modify the deployment preparation step
3. Commit and push
4. Workflow will auto-update on next run

### Troubleshooting

#### Deployment Fails

1. Check HF_TOKEN secret is set correctly
2. Verify Hugging Face Space exists
3. Check workflow logs for errors
4. Ensure token has write permissions

#### Space Not Updating

1. Check if workflow is running (Actions tab)
2. Verify no errors in workflow logs
3. Manually trigger workflow
4. Check Hugging Face Space build logs

#### App Not Loading

1. Check Dockerfile syntax
2. Verify requirements.txt has correct dependencies
3. Check Hugging Face Space logs
4. Test locally with Docker

## 📊 Monitoring

### GitHub Actions

View workflow runs:
- Go to Actions tab
- Select "Bridge to Hugging Face - Mapping and Inventory"
- View run history and logs

### Hugging Face

View deployment status:
- Go to [Hugging Face Space](https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory)
- Check "Logs" tab
- Monitor build status

## 🔐 Security

- HF_TOKEN is stored as GitHub secret (encrypted)
- Token is not exposed in logs
- Only authorized users can trigger workflow
- Workflow runs in isolated environment

## 📝 Notes

- The bridge maintains a connection between repos without modifying the original mapping-and-inventory repository
- All Hugging Face-specific files are created in the temporary workspace
- The original repository remains clean and unmodified
- Sync is one-way: mapping-and-inventory → Hugging Face

## 🎯 Next Steps

1. ✅ Git remote configured
2. ✅ Sync script created
3. ✅ GitHub Actions workflow set up
4. ⏳ Add HF_TOKEN secret (manual step)
5. ⏳ Create Hugging Face Space (manual step)
6. ⏳ Run first deployment

## 📞 Support

For issues or questions:
- Check workflow logs in GitHub Actions
- Review Hugging Face Space logs
- Consult this documentation
- Check Hugging Face Spaces documentation: [https://huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)

---

**Status:** ✅ Bridge tunnel infrastructure ready
**Last Updated:** 2026-04-05
**Maintained By:** DJ-Goana-Coding
