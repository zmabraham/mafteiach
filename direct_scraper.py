#!/usr/bin/env python3
"""
Mafteiach.app Direct Scraper
Scrapes by fetching JavaScript files and extracting entry IDs
"""

import requests
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path

DB_PATH = 'mafteiach.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def extract_entries_from_js(year):
    """Extract entry data from a year's JavaScript file"""
    url = f"https://www.mafteiach.app/all/by_year/{year}.js"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"  Error fetching {year}: {e}")
        return []

    # Extract all unique farbrengen IDs
    ids = re.findall(r'farbrengen_(\d+)', content)
    unique_ids = sorted(set(int(id) for id in ids))

    return unique_ids

def scrape_all_years():
    """Scrape all years"""
    # Years: 5690_5710 (combined), then 5710-5752
    years = [5690_5710] + list(range(5710, 5753))

    print(f"Mafteiach.app Direct Scraper")
    print(f"=" * 60)
    print(f"Scraping {len(years)} years...")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    conn = get_db()
    total_entries = 0

    for i, year in enumerate(years, 1):
        print(f"[{i}/{len(years)}] Year {year}...", end=" ", flush=True)

        entry_ids = extract_entries_from_js(year)

        if entry_ids:
            # Insert entries into database
            count = 0
            for entry_id in entry_ids:
                try:
                    # Parse the year for Hebrew date
                    # Entry IDs are sequential and contain date info
                    # For now, store minimal info
                    conn.execute('''
                        INSERT OR IGNORE INTO entries (
                            hebrew_year, entry_url, page_url,
                            title, processing_status
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        year if year < 6000 else 5711,  # Approximate
                        f"https://www.mafteiach.app/farbrengen/{entry_id}",
                        f"https://www.mafteiach.app/farbrengen/{entry_id}",
                        f"Farbrengen {entry_id}",
                        'discovered'
                    ))
                    count += 1
                except sqlite3.IntegrityError:
                    pass

            conn.commit()
            print(f"✓ {count} entries")
            total_entries += count
        else:
            print("✗ No entries")

        # Small delay between requests
        if i < len(years):
            time.sleep(0.5)

    conn.close()

    print()
    print("=" * 60)
    print(f"Complete! Found {total_entries} entries total")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    scrape_all_years()
