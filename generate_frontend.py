#!/usr/bin/env python3
"""
Generate GitHub Pages frontend with embedded data
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = '/workspace/group/mafteiach_scraper/mafteiach.db'
OUTPUT_DIR = '/workspace/group/mafteiach_scraper/frontend'

def generate_frontend():
    """Generate the frontend HTML with embedded data"""

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Fetch all entries
    entries = conn.execute('''
        SELECT * FROM entries
        ORDER BY hebrew_year, sequence
    ''').fetchall()

    # Get stats
    stats = conn.execute('''
        SELECT hebrew_year, COUNT(*) as count
        FROM entries
        WHERE hebrew_year IS NOT NULL
        GROUP BY hebrew_year
        ORDER BY hebrew_year
    ''').fetchall()

    # Prepare data
    entries_data = []
    years_set = set()

    for entry in entries:
        entry_dict = {
            'id': entry['id'],
            'hebrew_year': entry['hebrew_year'],
            'title': entry['title'] or f"Entry {entry['id']}",
            'entry_url': entry['entry_url'],
            'occasion_he': entry['occasion_he'],
            'occasion_en': entry['occasion_en']
        }
        entries_data.append(entry_dict)
        if entry['hebrew_year']:
            years_set.add(str(entry['hebrew_year']))

    stats_data = {
        'total': len(entries_data),
        'years': sorted(years_set),
        'generated': datetime.now().isoformat()
    }

    # Read the HTML template
    html_path = Path(OUTPUT_DIR) / 'index.html'
    html_content = html_path.read_text(encoding='utf-8')

    # Inject the data
    data_json = json.dumps({
        'entries': entries_data,
        'stats': stats_data
    }, ensure_ascii=False, indent=2)

    # Replace the placeholder data
    html_content = html_content.replace(
        '{"entries": [], "stats": {"total": 0, "years": []}}',
        data_json
    )

    # Write the generated HTML
    output_path = Path(OUTPUT_DIR) / 'index.html'
    output_path.write_text(html_content, encoding='utf-8')

    conn.close()

    print(f"✓ Generated frontend with {len(entries_data)} entries")
    print(f"  Output: {output_path.absolute()}")
    print(f"  Total size: {len(html_content):,} bytes")
    print(f"  Years: {len(years_set)}")

    return output_path

if __name__ == '__main__':
    generate_frontend()
