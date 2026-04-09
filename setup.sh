#!/bin/bash
# Setup script for Where Is My Space? repository
# This script initializes git and prepares the repository for upload to GitHub

set -e

echo "=========================================="
echo "Where Is My Space? - Repository Setup"
echo "=========================================="
echo ""
echo "This repository contains a universal disk space analysis tool"
echo "that works on any Linux system."
echo ""
echo "Author: Jukrapope Jitpimolmard"
echo ""

# Check if we're in the right directory
if [ ! -f "where_is_my_space.py" ]; then
    echo "Error: Please run this script from the Where_is_my_space directory"
    exit 1
fi

echo "Step 1: Initializing git repository..."
git init

echo ""
echo "Step 2: Adding all files..."
git add .

echo ""
echo "Step 3: Creating initial commit..."
git commit -m "Initial commit: Where Is My Space? disk analysis tool"

echo ""
echo "=========================================="
echo "Repository initialized successfully!"
echo "=========================================="
echo ""
echo "About the tool:"
echo "- Works on any Linux system"
echo "- No hardcoded paths or system-specific configurations"
echo "- Configurable mount point exclusions"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub (https://github.com/new)"
echo "2. Run the following commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/where-is-my-space.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Replace YOUR_USERNAME with your GitHub username."
echo ""
echo "For more information, see:"
echo "- README.md - Full documentation"
echo "- QUICK_START.md - Quick reference"
echo "- REPO_SETUP.md - Repository setup guide"
