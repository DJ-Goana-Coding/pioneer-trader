#!/bin/bash

# 🌉 Bridge Script: Sync mapping-and-inventory to Hugging Face Space
# This script creates a bridge between the mapping-and-inventory GitHub repo
# and the Mapping-and-Inventory Hugging Face Space

set -e

echo "🌉 BRIDGE TUNNEL: Connecting mapping-and-inventory to Hugging Face"
echo "=================================================================="

# Configuration
REPO_NAME="mapping-and-inventory"
HF_SPACE_NAME="Mapping-and-Inventory"
HF_USERNAME="${HF_USERNAME:-DJ-Goana-Coding}"
TEMP_DIR="/tmp/${REPO_NAME}-hf-bridge"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Fetch latest from mapping-and-inventory repo
echo -e "${BLUE}Step 1: Fetching latest content from mapping-and-inventory repository...${NC}"
git fetch mapping-and-inventory main

# Step 2: Create a temporary directory for the bridge
echo -e "${BLUE}Step 2: Creating bridge workspace...${NC}"
rm -rf "${TEMP_DIR}"
mkdir -p "${TEMP_DIR}"

# Step 3: Clone the mapping-and-inventory content
echo -e "${BLUE}Step 3: Cloning mapping-and-inventory repository...${NC}"
git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git "${TEMP_DIR}"

cd "${TEMP_DIR}"

# Step 4: Check if Hugging Face Space exists, if not provide instructions
echo -e "${BLUE}Step 4: Preparing Hugging Face deployment...${NC}"

# Create README with Hugging Face metadata if it doesn't exist
if ! grep -q "^---" README.md 2>/dev/null; then
    echo -e "${YELLOW}Adding Hugging Face metadata to README.md...${NC}"

    # Backup original README
    if [ -f README.md ]; then
        cp README.md README.md.bak
    fi

    # Create new README with Hugging Face frontmatter
    cat > README.md << 'EOF'
---
title: Mapping and Inventory
emoji: 🗺️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# 🗺️ Mapping and Inventory

A comprehensive mapping and inventory system for the Citadel Omega ecosystem.

## 📚 Documentation

This space contains extensive documentation and architectural guides for:

- Citadel Omega Architecture
- Agent Legion Systems
- Omnidimensional Infrastructure
- Character Discovery and Activation
- Deployment Guides
- And much more...

## 🚀 Deployment

This space is deployed using Docker. See the Dockerfile for configuration details.

## 📖 Browse Documentation

Navigate through the files to explore the complete documentation set.

EOF

    # Append original README content if it existed
    if [ -f README.md.bak ]; then
        echo "" >> README.md
        echo "---" >> README.md
        echo "" >> README.md
        cat README.md.bak >> README.md
    fi
fi

# Create or update Dockerfile for Hugging Face Spaces
echo -e "${YELLOW}Creating Dockerfile for Hugging Face deployment...${NC}"
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install basic dependencies
RUN pip install --no-cache-dir gradio huggingface-hub

# Copy all documentation
COPY . .

# Create a simple Gradio app to browse documentation
RUN echo 'import gradio as gr\n\
import os\n\
from pathlib import Path\n\
\n\
def list_files():\n\
    """List all markdown files in the repository"""\n\
    md_files = sorted([str(p) for p in Path(".").rglob("*.md")])\n\
    return md_files\n\
\n\
def read_file(filepath):\n\
    """Read and return file contents"""\n\
    try:\n\
        with open(filepath, "r", encoding="utf-8") as f:\n\
            return f.read()\n\
    except Exception as e:\n\
        return f"Error reading file: {e}"\n\
\n\
# Create Gradio interface\n\
with gr.Blocks(title="Mapping and Inventory Documentation") as demo:\n\
    gr.Markdown("# 🗺️ Mapping and Inventory - Documentation Browser")\n\
    gr.Markdown("Browse through the comprehensive documentation of the Citadel Omega ecosystem.")\n\
    \n\
    with gr.Row():\n\
        file_list = gr.Dropdown(\n\
            choices=list_files(),\n\
            label="Select Documentation File",\n\
            interactive=True\n\
        )\n\
    \n\
    content_display = gr.Markdown(label="Content")\n\
    \n\
    file_list.change(fn=read_file, inputs=file_list, outputs=content_display)\n\
\n\
if __name__ == "__main__":\n\
    demo.launch(server_name="0.0.0.0", server_port=7860)\n\
' > app.py

# Install requirements
RUN pip install --no-cache-dir gradio

EXPOSE 7860

CMD ["python", "app.py"]
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
gradio>=4.0.0
huggingface-hub>=0.19.0
EOF

echo -e "${GREEN}✅ Bridge workspace prepared successfully!${NC}"
echo ""
echo -e "${YELLOW}📋 NEXT STEPS TO DEPLOY TO HUGGING FACE:${NC}"
echo ""
echo "1. Create a Hugging Face Space:"
echo "   - Go to: https://huggingface.co/new-space"
echo "   - Name: ${HF_SPACE_NAME}"
echo "   - SDK: Docker"
echo "   - Visibility: Public or Private"
echo ""
echo "2. Push this repository to Hugging Face:"
echo "   cd ${TEMP_DIR}"
echo "   git remote add huggingface https://huggingface.co/spaces/${HF_USERNAME}/${HF_SPACE_NAME}"
echo "   git add -A"
echo "   git commit -m \"Deploy mapping-and-inventory to Hugging Face Space\""
echo "   git push huggingface main"
echo ""
echo "3. Or use the Hugging Face CLI:"
echo "   pip install huggingface-hub[cli]"
echo "   huggingface-cli login"
echo "   huggingface-cli upload ${HF_USERNAME}/${HF_SPACE_NAME} . --repo-type=space"
echo ""
echo -e "${BLUE}Bridge tunnel ready at: ${TEMP_DIR}${NC}"
echo ""
echo "The modified repository with Hugging Face deployment files is ready."
echo "Files created/modified:"
echo "  - README.md (with HF metadata)"
echo "  - Dockerfile (Gradio documentation browser)"
echo "  - requirements.txt"
echo "  - app.py (auto-generated in Dockerfile)"
