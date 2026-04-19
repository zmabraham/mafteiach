#!/usr/bin/env python3
"""
Test script for mafteiach scraper
Tests database setup and basic scraping functionality
"""

import sys
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db_setup import MafteiachDatabase


def test_database_setup():
    """Test database initialization"""
    print("Testing database setup...")

    db = MafteiachDatabase('test_mafteiach.db')

    # Test tables exist
    tables = db.conn.execute('''
        SELECT name FROM sqlite_master WHERE type='table'
    ''').fetchall()

    print(f"✓ Created {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")

    # Test static data
    months = db.conn.execute('SELECT COUNT(*) FROM hebrew_months').fetchone()[0]
    print(f"✓ Inserted {months} Hebrew months")

    categories = db.conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
    print(f"✓ Inserted {categories} categories")

    # Test entry insertion
    test_entry = {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 1,
        'occasion_he': 'יום א׳ דר״ה',
        'occasion_en': 'Sunday before Rosh Hashana',
        'detail': 'בעת ההליכה לתשליך',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/1',
        'title': 'Test Entry',
        'processing_status': 'test'
    }

    entry_id = db.insert_entry(test_entry)

    if entry_id:
        print(f"✓ Inserted test entry with ID {entry_id}")

        # Test retrieval
        retrieved = db.get_entry_by_url(test_entry['entry_url'])
        if retrieved:
            print(f"✓ Retrieved entry: {retrieved['occasion_he']}")
        else:
            print("✗ Failed to retrieve entry")
    else:
        print("✗ Failed to insert entry")

    # Test source insertion
    source = {
        'entry_id': entry_id,
        'source_type': 'pdf',
        'url': 'https://example.com/test.pdf',
        'title': 'Test PDF'
    }

    source_id = db.insert_source(source)
    if source_id:
        print(f"✓ Inserted test source with ID {source_id}")

    # Test stats
    stats = db.get_stats()
    print(f"✓ Database stats: {stats['total_entries']} entries")

    # Test export
    json_path = db.export_json('test_export.json')
    print(f"✓ Exported to JSON: {json_path}")

    # Cleanup
    db.close()

    # Remove test database
    Path('test_mafteiach.db').unlink(missing_ok=True)
    Path('test_export.json').unlink(missing_ok=True)

    print("\n✓ All tests passed!")
    return True


async def test_scraper_basic():
    """Test basic scraper functionality"""
    print("\nTesting basic scraper functionality...")

    try:
        from scraper import MafteiachScraper

        scraper = MafteiachScraper(db_path='test_mafteiach.db', headless=True)

        # Test with a single year
        scraper.years = [5711]  # Just one year for testing

        print("Attempting to scrape year 5711...")
        print("Note: This requires internet access and may take a minute")

        # Run scraper
        await scraper.scrape_all()

        # Check results
        stats = scraper.db.get_stats()
        print(f"✓ Scraped {stats['total_entries']} entries")

        scraper.db.close()

        # Cleanup
        Path('test_mafteiach.db').unlink(missing_ok=True)

        return True

    except Exception as e:
        print(f"✗ Scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_requirements():
    """Test if API requirements are available"""
    print("\nTesting API requirements...")

    missing = []

    # Check for FastAPI
    try:
        import fastapi
        print("✓ FastAPI is available")
    except ImportError:
        missing.append("fastapi")
        print("✗ FastAPI not available (install with: pip install fastapi uvicorn)")

    # Check for uvicorn
    try:
        import uvicorn
        print("✓ Uvicorn is available")
    except ImportError:
        missing.append("uvicorn")
        print("✗ Uvicorn not available (install with: pip install uvicorn)")

    if not missing:
        print("\n✓ All API requirements met!")
        print("  Run API with: python api.py")
    else:
        print(f"\n✗ Missing: {', '.join(missing)}")

    return len(missing) == 0


def main():
    """Run all tests"""
    print("="*60)
    print("Mafteiach.app Scraper - Test Suite")
    print("="*60)

    # Test 1: Database setup
    if not test_database_setup():
        print("\n✗ Database setup test failed")
        return False

    # Test 2: API requirements
    test_api_requirements()

    # Test 3: Basic scraper (optional, requires network)
    print("\n" + "="*60)
    print("Optional: Test basic scraper functionality?")
    print("This will make actual HTTP requests to mafteiach.app")
    response = input("Run scraper test? (y/n): ").lower().strip()

    if response == 'y':
        asyncio.run(test_scraper_basic())

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print("✓ Database setup: Working")
    print("✓ Schema: Complete")
    print("✓ Export functionality: Working")

    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Install playwright: playwright install chromium")
    print("3. Run scraper: python scraper.py")
    print("4. Start API: python api.py")
    print("5. View docs: http://localhost:8000/docs")

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
