#!/usr/bin/env python3
"""
Mafteiach.app JavaScript Scraper
Parses JavaScript endpoints to extract entry data
"""

import requests
import re
import json
import time
from datetime import datetime
from html import unescape
from urllib.parse import urljoin

from db_setup import MafteiachDatabase


class MafteiachJSScraper:
    def __init__(self, db_path='mafteiach.db'):
        self.db = MafteiachDatabase(db_path)
        self.base_url = 'https://www.mafteiach.app'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

        # Years: 5690_5710 (combined early), then 5710-5752
        self.years = [5690_5710] + list(range(5710, 5753))

        # Month mapping
        self.month_map = {
            'תשרי': 'teshre',
            'חשון': 'cheshvan',
            'כסלו': 'kislev',
            'טבת': 'teves',
            'שבט': 'shevat',
            'אדר ראשון': 'adar_1',
            'אדר שני': 'adar_2',
            'אדר': 'adar',
            'ניסן': 'nissan',
            'אייר': 'iyar',
            'סיון': 'sivan',
            'תמוז': 'tammuz',
            'אב': 'av',
            'אלול': 'elul',
        }

    def fetch_year_js(self, year):
        """Fetch the JavaScript for a year"""
        url = f"{self.base_url}/all/by_year/{year}.js?include_right_nav=false"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  Error fetching {year}: {e}")
            self.db.log('error', f'Failed to fetch year {year}', {'error': str(e)})
            return None

    def extract_html_from_js(self, js_content):
        """Extract the HTML content from JavaScript response"""
        # Look for the HTML string in the JavaScript
        # Pattern: html = "...big html string...";

        # Find the HTML assignment
        match = re.search(r'html\s*=\s*"((?:[^"\\]|\\.)*)"', js_content, re.DOTALL)
        if match:
            html = match.group(1)
            # The HTML is escaped with backslashes, need to unescape properly
            # Replace common escape sequences
            html = html.replace(r'\n', '\n')
            html = html.replace(r'\t', '\t')
            html = html.replace(r'\\"', '"')
            html = html.replace(r"\\'", "'")
            html = html.replace(r'\\', '\\')  # Handle double backslashes
            html = unescape(html)
            return html

        return None

    def parse_entries_from_html(self, html, year):
        """Parse entries from the extracted HTML"""
        entries = []

        # Extract month sections
        # Pattern: <div id="month_X"> with Hebrew month name
        month_pattern = r'<div[^>]*id="month_\d+"[^>]*class="[^"]*month[^"]*"[^>]*>\s*<button[^>]*>([^<]+)</button>'

        # Also look for collapsible buttons with Hebrew text
        hebrew_text_pattern = r'[\u0590-\u05FF\s\'".,]+'

        # Find farbrengen (entry) sections
        # Pattern: loadFarbrengenFragment(event, ID, false, 'DATE')
        entry_pattern = r"loadFarbrengenFragment\(([^)]+)\)"

        # Extract all entry calls
        for match in re.finditer(entry_pattern, html):
            params = match.group(1)
            # Parse: event, ID, false, 'YYYY-MM-DD'
            param_match = re.search(r'event,\s*(\d+),\s*false,\s*[\'"](\d+-\d+-\d+)[\'"]', params)
            if param_match:
                entry_id = param_match.group(1)
                date_str = param_match.group(2)  # YYYY-MM-DD

                # Extract the Hebrew text from the button
                # Look for the button text before this loadFarbrengenFragment call
                before_text = html[max(0, match.start()-500):match.start()]
                text_match = re.search(r'<span[^>]*class="[^"]*collapsible-button-arrow[^"]*"[^>]*>.*?</span>\s*([\u0590-\u05FF\s\'".,]+)', before_text)
                if text_match:
                    hebrew_text = text_match.group(1).strip()
                    # Clean up HTML entities
                    hebrew_text = hebrew_text.replace('&quot;', '"').replace('&#39;', "'").replace('&amp;', '&')

                    # Parse date
                    year_part, month_part, day_part = date_str.split('-')

                    entry = {
                        'hebrew_year': int(year_part),
                        'hebrew_day': int(day_part) if day_part.isdigit() else None,
                        'entry_url': f"{self.base_url}/farbrengen/{entry_id}",
                        'page_url': f"{self.base_url}/farbrengen/{entry_id}",
                        'title': hebrew_text,
                        'occasion_he': hebrew_text,
                        'processing_status': 'discovered',
                        'detail': date_str
                    }

                    entries.append(entry)

        # Also try to find month names and associate entries
        current_month = None
        for line in html.split('\n'):
            # Look for month buttons
            month_match = re.search(r'<button[^>]*>([\u0590-\u05FF\s]+)</button>', line)
            if month_match:
                text = month_match.group(1).strip()
                # Check if it's a Hebrew month
                for month in self.month_map.keys():
                    if month in text:
                        current_month = month
                        break

            # Update entries with month info
            if current_month:
                for entry in entries:
                    if 'hebrew_month' not in entry:
                        entry['hebrew_month'] = current_month
                        entry['hebrew_month_translit'] = self.month_map.get(current_month)

        return entries

    def scrape_year(self, year):
        """Scrape all entries for a specific year"""
        print(f"\n{'='*60}")
        print(f"Scraping year {year}")
        print(f"{'='*60}")

        js_content = self.fetch_year_js(year)
        if not js_content:
            return []

        # Extract HTML from JavaScript
        html = self.extract_html_from_js(js_content)
        if not html:
            print("  Could not extract HTML from JavaScript")
            return []

        # Parse entries
        entries = self.parse_entries_from_html(html, year)

        # Store in database
        count = 0
        for entry in entries:
            entry_id = self.db.insert_entry(entry)
            if entry_id:
                count += 1

        print(f"  Found {count} entries")
        return entries

    def scrape_all(self):
        """Main scraping routine"""
        start_time = datetime.now()

        print(f"{'='*70}")
        print(f"Mafteiach.app JavaScript Scraper")
        print(f"{'='*70}")
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Years to scrape: {len(self.years)}")
        print(f"Database: {self.db.db_path}")
        print(f"{'='*70}")

        total_entries = 0

        for i, year in enumerate(self.years, 1):
            print(f"\n[{i}/{len(self.years)}] Processing year {year}...")

            entries = self.scrape_year(year)
            total_entries += len(entries)

            # Print progress
            stats = self.db.get_stats()
            print(f"\nProgress: {stats['total_entries']} total entries in database")

            # Be respectful - add delay between requests
            if i < len(self.years):
                time.sleep(1)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n{'='*70}")
        print(f"Scraping Complete!")
        print(f"{'='*70}")
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"Total entries scraped: {total_entries}")
        print(f"\nFinal Statistics:")
        stats = self.db.get_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in list(value.items())[:10]:
                    print(f"    {k}: {v}")
                if len(value) > 10:
                    print(f"    ... and {len(value) - 10} more")
            else:
                print(f"  {key}: {value}")

        return stats


def main():
    """Main entry point"""
    scraper = MafteiachJSScraper()

    # Scrape all years
    stats = scraper.scrape_all()

    # Export data
    print("\nExporting data...")
    json_path = scraper.db.export_json('mafteiach_export.json')
    csv_path = scraper.db.export_csv('mafteiach_export.csv')

    print(f"\nExported to:")
    print(f"  JSON: {json_path}")
    print(f"  CSV: {csv_path}")

    scraper.db.close()


if __name__ == '__main__':
    main()
