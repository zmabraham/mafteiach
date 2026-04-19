#!/bin/bash
# Mafteiach.app Scraper - Quick Start Script

set -e

echo "=========================================="
echo "Mafteiach.app Scraper - Quick Start"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 required"; exit 1; }

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium

# Initialize database
echo ""
echo "Initializing database..."
python db_setup.py

# Run tests
echo ""
echo "Running tests..."
python test_scraper.py << EOF
n
EOF

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Run the scraper:"
echo "   python scraper.py"
echo ""
echo "2. Start the API server:"
echo "   python api.py"
echo ""
echo "3. Open the web interface:"
echo "   Open web_interface.html in your browser"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "Files created:"
echo "  - mafteiach.db (SQLite database)"
echo "  - mafteiach_export.json (JSON export)"
echo "  - mafteiach_export.csv (CSV export)"
echo ""
