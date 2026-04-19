#!/usr/bin/env python3
"""
Mafteiach.app Simple Scraper
Uses requests + BeautifulSoup instead of Playwright
More suitable for containerized environments
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import sqlite3
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path

from db_setup import MafteiachDatabase


class MafteiachSimpleScraper:
    def __init__(self, db_path='mafteiach.db'):
        self.db = MafteiachDatabase(db_path)
        self.base_url = 'https://www.mafteiach.app'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # Year range: תר"צ (5690) - תשנ"ב (5752)
        # Combined range at start: 5690_5710, then individual years 5710-5752
        self.years = [5690_5710] + list(range(5710, 5753))

    def fetch_year_page(self, year):
        """Fetch a year page and return the HTML content"""
        url = f"{self.base_url}/all/by_year/{year}"
        print(f"  Fetching: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  Error fetching year {year}: {e}")
            self.db.log('error', f'Failed to fetch year {year}', {'error': str(e)})
            return None

    def parse_year_html(self, html, year):
        """Parse entries from year page HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        entries = []

        # Find all month sections
        # Look for Hebrew month names in headings
        hebrew_months = [
            'תשרי', 'חשון', 'כסלו', 'טבת', 'שבט',
            'אדר ראשון', 'אדר שני', 'אדר',
            'ניסן', 'אייר', 'סיון', 'תמוז', 'אב', 'אלול'
        ]

        current_month = None
        sequence = 0

        # Look for text content containing entries
        # The site uses JavaScript to render, so we need to find patterns
        # in the HTML/scripts

        # Try to find data in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # Look for Hebrew content in scripts
                for month in hebrew_months:
                    if month in script.string:
                        # Extract entries for this month
                        month_pattern = re.escape(month)
                        # Look for patterns around the month name
                        matches = re.finditer(
                            rf'{month_pattern}.*?(?={"|".join(map(re.escape, hebrew_months))}|$)',
                            script.string,
                            re.DOTALL
                        )
                        # This is a simplified approach

        # Better approach: Look for links in the page
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            text = link.get_text(strip=True)

            # Parse entry URLs like /sichos/5711/teshre/1
            match = re.match(r'/(\w+)/(\d{4})/(\w+)/(\d+)', href)
            if match:
                category, year_num, month_translit, seq = match.groups()

                # Map transliteration to Hebrew
                month_map = {
                    'teshre': 'תשרי',
                    'cheshvan': 'חשון',
                    'kislev': 'כסלו',
                    'teves': 'טבת',
                    'shevat': 'שבט',
                    'adar_1': 'אדר ראשון',
                    'adar_2': 'אדר שני',
                    'adar': 'אדר',
                    'nissan': 'ניסן',
                    'iyar': 'אייר',
                    'sivan': 'סיון',
                    'tammuz': 'תמוז',
                    'av': 'אב',
                    'elul': 'אלול',
                }

                entry = {
                    'hebrew_year': int(year_num),
                    'hebrew_month': month_map.get(month_translit, month_translit),
                    'hebrew_month_translit': month_translit,
                    'sequence': int(seq),
                    'category': category,
                    'entry_url': urljoin(self.base_url, href),
                    'page_url': urljoin(self.base_url, href),
                    'title': text or f'{category} {year_num}/{month_translit}/{seq}',
                    'processing_status': 'discovered'
                }

                entries.append(entry)

        # If no links found, try to parse from page structure
        if not entries:
            # Look for list items, divs with specific patterns
            for element in soup.find_all(['li', 'div', 'p']):
                text = element.get_text(strip=True)
                # Look for Hebrew date patterns
                if any(month in text for month in hebrew_months[:3]):  # Start with Tishrei
                    for month in hebrew_months:
                        if month in text:
                            current_month = month
                            break

        return entries

    def parse_js_content(self, html):
        """Parse content from JavaScript in HTML"""
        # Look for data in JavaScript variables
        entries = []

        # Pattern to find JavaScript data
        patterns = [
            r'innerHTML\s*=\s*["\']([^"\']+)',
            r'data\s*[:=]\s*(\[[^\]]+\}|\{[^\}]+\})',
            r'entries\s*[:=]\s*(\[[^\]]+\])',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                try:
                    # Try to parse as JSON
                    if isinstance(match, str):
                        # Unescape if needed
                        match = match.replace('\\"', '"').replace('\\/', '/')

                    # Look for URLs and Hebrew content
                    urls = re.findall(r'(/sichos/\d+/\w+/\d+)', match)
                    hebrew = re.findall(r'([\u0590-\u05FF\s]{10,})', match)

                    if urls and hebrew:
                        entries.append({
                            'urls': urls,
                            'hebrew': hebrew
                        })
                except:
                    pass

        return entries

    def scrape_year(self, year):
        """Scrape all entries for a specific year"""
        print(f"\n{'='*60}")
        print(f"Scraping year {year}")
        print(f"{'='*60}")

        html = self.fetch_year_page(year)
        if not html:
            return []

        entries = self.parse_year_html(html, year)

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
        print(f"Mafteiach.app Simple Scraper")
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
                time.sleep(2)

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
    scraper = MafteiachSimpleScraper()

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
