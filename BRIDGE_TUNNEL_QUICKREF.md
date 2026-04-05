# 🌉 Bridge Tunnel - Quick Reference

## Quick Commands

### Check Bridge Status
```bash
git remote -v | grep mapping-and-inventory
```

### Manual Sync
```bash
./scripts/sync_mapping_to_huggingface.sh
```

### Deploy to Hugging Face (Manual)
```bash
# After running sync script
cd /tmp/mapping-and-inventory-hf-bridge

# Option 1: Git Push
git remote add huggingface https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory
git add -A
git commit -m "Deploy to HF Space"
git push huggingface main

# Option 2: HF CLI
pip install huggingface-hub[cli]
huggingface-cli login
huggingface-cli upload DJ-Goana-Coding/Mapping-and-Inventory . --repo-type=space
```

### Trigger Auto-Deploy
1. Go to GitHub Actions
2. Select "Bridge to Hugging Face - Mapping and Inventory"
3. Click "Run workflow"

## Setup Checklist

- [x] Git remote configured
- [x] Sync script created (`scripts/sync_mapping_to_huggingface.sh`)
- [x] GitHub Actions workflow ready (`.github/workflows/sync-mapping-to-huggingface.yml`)
- [ ] Add `HF_TOKEN` secret to GitHub repo settings
- [ ] Create Hugging Face Space: `Mapping-and-Inventory`
- [ ] Run first deployment

## Key Files

| File | Purpose |
|------|---------|
| `scripts/sync_mapping_to_huggingface.sh` | Manual sync script |
| `.github/workflows/sync-mapping-to-huggingface.yml` | Automated deployment workflow |
| `BRIDGE_TUNNEL_GUIDE.md` | Complete documentation |

## URLs

- **Source:** https://github.com/DJ-Goana-Coding/mapping-and-inventory
- **Destination:** https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory
- **This Repo:** https://github.com/DJ-Goana-Coding/pioneer-trader

## Troubleshooting

**Issue:** Workflow not deploying
**Fix:** Add HF_TOKEN secret in repo settings → Secrets and variables → Actions

**Issue:** Space not found
**Fix:** Create space at https://huggingface.co/new-space (name: Mapping-and-Inventory, SDK: Docker)

**Issue:** Permission denied
**Fix:** Ensure HF token has write permissions

## Next Steps

1. **Create Hugging Face Space:**
   - Visit: https://huggingface.co/new-space
   - Name: `Mapping-and-Inventory`
   - SDK: `Docker`

2. **Add Token:**
   - Get token: https://huggingface.co/settings/tokens
   - Add to GitHub: Repo Settings → Secrets → New secret
   - Name: `HF_TOKEN`

3. **Deploy:**
   - Option A: Trigger workflow manually
   - Option B: Run `./scripts/sync_mapping_to_huggingface.sh` and follow instructions

---

For full documentation, see: `BRIDGE_TUNNEL_GUIDE.md`
