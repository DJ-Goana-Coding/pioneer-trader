#!/bin/bash

# Script to connect to mapping-and-inventory repository
# This establishes the connection mentioned in SESSION_28_COMPLETE.md

echo "🛰️ T.I.A. CONNECTION PROTOCOL: Establishing link to mapping-and-inventory..."

# Check if mapping-and-inventory exists as a git submodule or separate repo
if [ -d "/home/runner/work/pioneer-trader/pioneer-trader/mapping-and-inventory/.git" ]; then
    echo "✅ mapping-and-inventory is a git submodule"
    cd mapping-and-inventory
    git status
else
    echo "📂 mapping-and-inventory is a regular directory, not a git repository"
    echo "Creating git repository connection..."
    
    # Try to clone the mapping-and-inventory repository
    if git ls-remote https://github.com/DJ-Goana-Coding/mapping-and-inventory.git &> /dev/null; then
        echo "✅ Found mapping-and-inventory repository on GitHub"
        echo "URL: https://github.com/DJ-Goana-Coding/mapping-and-inventory.git"
        
        # Back up existing directory if it exists
        if [ -d "/home/runner/work/pioneer-trader/pioneer-trader/mapping-and-inventory" ]; then
            echo "📦 Backing up existing mapping-and-inventory directory..."
            mv /home/runner/work/pioneer-trader/pioneer-trader/mapping-and-inventory /home/runner/work/pioneer-trader/pioneer-trader/mapping-and-inventory.backup
        fi
        
        # Clone the repository
        cd /home/runner/work/pioneer-trader/pioneer-trader
        git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
        echo "✅ mapping-and-inventory repository cloned successfully"
    else
        echo "⚠️ mapping-and-inventory repository not found on GitHub"
        echo "You may need to create it first or check the repository name"
    fi
fi

echo "🛡️ Connection protocol complete"
