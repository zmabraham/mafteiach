#!/usr/bin/env python3
"""
Generate GitHub Pages frontend with embedded data
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

DB_PATH = '/workspace/group/mafteiach_scraper/mafteiach.db'
OUTPUT_DIR = '/workspace/group/mafteiach_scraper/frontend'

def get_category_from_url(url):
    """Extract category from URL path"""
    if not url:
        return 'other'
    try:
        path = urlparse(url).path
        parts = path.split('/')
        if len(parts) > 1:
            return parts[1]
    except:
        pass
    return 'other'

def format_hebrew_year(year):
    """Convert Hebrew year to traditional format"""
    if not year:
        return ''
    year_str = str(year)
    # Convert to Hebrew letters format (thousands + hundreds)
    thousands = year_str[0]  # 5 for 57xx
    rest = int(year_str[1:])  # remainder

    hebrew_digits = {
        1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט',
        10: 'י', 20: 'כ', 30: 'ל', 40: 'מ', 50: 'נ', 60: 'ס', 70: 'ע', 80: 'פ', 90: 'צ',
        100: 'ק', 200: 'ר', 300: 'ש', 400: 'ת'
    }

    # Simple version - just use the numeric format with quotes
    return year_str

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
    categories_set = set()
    months_set = set()
    occasions_set = set()

    for entry in entries:
        # Derive category from URL for better accuracy
        url_category = get_category_from_url(entry['entry_url'] or entry['page_url'])

        entry_dict = {
            'id': entry['id'],
            'hebrew_year': entry['hebrew_year'],
            'hebrew_year_display': format_hebrew_year(entry['hebrew_year']),
            'hebrew_month': entry['hebrew_month'],
            'hebrew_month_translit': entry['hebrew_month_translit'],
            'gregorian_year': entry['gregorian_year'],
            'category': url_category,
            'subcategory': entry['subcategory'],
            'sequence': entry['sequence'],
            'occasion_he': entry['occasion_he'],
            'occasion_en': entry['occasion_en'],
            'detail': entry['detail'],
            'parsha': entry['parsha'],
            'title': entry['title'] or f"{url_category.capitalize()} {entry['id']}",
            'entry_url': entry['entry_url'],
            'page_url': entry['page_url'],
            'description': entry['description']
        }
        entries_data.append(entry_dict)
        if entry['hebrew_year']:
            years_set.add(str(entry['hebrew_year']))
        categories_set.add(url_category)
        if entry['hebrew_month']:
            months_set.add(entry['hebrew_month'])
        if entry['occasion_en']:
            occasions_set.add(entry['occasion_en'])

    # Build stats with Hebrew month names
    month_names = {
        'ניסן': 'Nissan', 'אייר': 'Iyar', 'סיון': 'Sivan', 'תמוז': 'Tammuz',
        'אב': 'Av', 'אלול': 'Elul', 'תשרי': 'Tishrei', 'חשון': 'Cheshvan',
        'כסלו': 'Kislev', 'טבת': 'Tevet', 'שבט': 'Shevat', 'אדר': 'Adar'
    }

    months_data = [{'he': m, 'en': month_names.get(m, m)} for m in sorted(months_set)]

    stats_data = {
        'total': len(entries_data),
        'years': sorted(years_set),
        'categories': sorted(categories_set),
        'months': months_data,
        'occasions': sorted(list(occasions_set))[:50],
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
