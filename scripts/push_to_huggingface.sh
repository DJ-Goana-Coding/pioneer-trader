#!/bin/bash

# Script to push repository to Hugging Face
# Based on HUGGINGFACE_DEPLOYMENT.md and sync_to_hf.yml

echo "🚀 T.I.A. DEPLOYMENT PROTOCOL: Pushing to Hugging Face..."

# Check if HF_TOKEN is set
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️ HF_TOKEN environment variable not set"
    echo "To push to Hugging Face, you need to:"
    echo "1. Get your Hugging Face token from https://huggingface.co/settings/tokens"
    echo "2. Set it as an environment variable: export HF_TOKEN='your_token_here'"
    echo "3. Or add it as a GitHub secret named HF_TOKEN"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Add Hugging Face remote if it doesn't exist
if ! git remote get-url hf &> /dev/null; then
    echo "➕ Adding Hugging Face remote..."
    git remote add hf https://DJ-Goana-Coding:$HF_TOKEN@huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader
    echo "✅ Hugging Face remote added"
else
    echo "✅ Hugging Face remote already exists"
fi

# Verify the connection
echo "🔍 Verifying Hugging Face connection..."
if git ls-remote hf &> /dev/null; then
    echo "✅ Connection to Hugging Face successful"
    
    # Push to Hugging Face
    echo "📤 Pushing to Hugging Face..."
    git push hf $CURRENT_BRANCH --force-with-lease
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed to Hugging Face!"
        echo "🌐 Your app should be available at:"
        echo "   https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader"
    else
        echo "❌ Failed to push to Hugging Face"
        exit 1
    fi
else
    echo "❌ Cannot connect to Hugging Face. Please check:"
    echo "   1. Your HF_TOKEN is valid"
    echo "   2. The Hugging Face Space exists: https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader"
    echo "   3. You have write access to the Space"
    exit 1
fi

echo "🛡️ Deployment protocol complete"
