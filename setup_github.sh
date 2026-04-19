#!/bin/bash
# Setup GitHub repository for mafteiach frontend

set -e

REPO_NAME="mafteiach"
GITHUB_USER="zmabraham"

echo "=========================================="
echo "Mafteiach - GitHub Repository Setup"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Mafteiach database with 3,350 entries

- Complete index of the Rebbe's Torah (1950-1992)
- 3,350 entries from mafteiach.app
- Self-contained frontend with embedded data
- GitHub Pages ready
"
else
    echo "Git already initialized"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Create repository on GitHub:"
echo "   https://github.com/new"
echo "   Repository name: $REPO_NAME"
echo "   Make it PUBLIC"
echo ""
echo "2. Add remote (replace with your token):"
echo "   git remote add origin https://<TOKEN>@github.com/$GITHUB_USER/$REPO_NAME.git"
echo ""
echo "   Or use SSH:"
echo "   git remote add origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
echo ""
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. Enable GitHub Pages:"
echo "   - Go to: https://github.com/$GITHUB_USER/$REPO_NAME/settings/pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main"
echo "   - Folder: /frontend"
echo ""
echo "5. Your site will be live at:"
echo "   https://$GITHUB_USER.github.io/$REPO_NAME/"
echo ""
echo "=========================================="
echo "Repository Contents:"
echo "=========================================="
echo ""
echo "Files in this directory:"
ls -lah | grep -v "^d" | grep -v "^total" | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Total size:"
du -sh . | awk '{print "  " $1}'
echo ""
echo "=========================================="
