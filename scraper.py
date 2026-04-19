#!/usr/bin/env python3
"""
Mafteiach.app Web Scraper
Scrapes all entries from mafteiach.app and stores in database
"""

import asyncio
import re
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Installing playwright...")
    import subprocess
    subprocess.run(['pip', 'install', 'playwright'], check=True)
    subprocess.run(['playwright', 'install', 'chromium'], check=True)
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from db_setup import MafteiachDatabase


class MafteiachScraper:
    def __init__(self, db_path='mafteiach.db', headless=True):
        self.db = MafteiachDatabase(db_path)
        self.base_url = 'https://www.mafteiach.app'
        self.headless = headless

        # Year range to scrape
        self.years = [5690_5710] + list(range(5710, 5753))  # All years

        # Month transliterations mapping
        self.month_translit = {
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

        # Parse Hebrew date codes
        self.date_patterns = {
            r'יום ([א-ת]\'?) דר"ה': 'Sunday before Rosh Hashana',
            r'ערב יו"כ': 'Erev Yom Kippur',
            r'מוצאי יו"כ': 'Motzai Yom Kippur',
            r'מוצאי ([א-ת]) דחה"ס': 'Motzai {day} Shabbos',
            r'ערב ר"ה': 'Erev Rosh Hashana',
            r'שבת חוה"מ': 'Shabbos Chol Hamoed',
            r'ליל ([\w"\'-]+)': 'Eve of {holiday}',
            r'יום ([\w"\'-]+)': 'Day of {holiday}',
            r'כ"([א-ת]+) ([\w"\'-]+)?': 'Date {day} of {month}',
        }

    async def scrape_year(self, year, page):
        """Scrape all entries for a specific year"""
        self.db.log('info', f'Starting year {year}', {'year': year})

        url = f"{self.base_url}/all/by_year/{year}"
        print(f"\n{'='*60}")
        print(f"Scraping year {year}")
        print(f"URL: {url}")
        print(f"{'='*60}")

        try:
            await page.goto(url, wait_until='networkidle', timeout=60000)

            # Wait for content to load
            await page.wait_for_selector('main, .content, .month-section, [class*="month"]',
                                        timeout=30000)

            # Give extra time for dynamic content
            await asyncio.sleep(3)

            # Get page content
            content = await page.content()

            # Parse entries from the page
            entries = await self.parse_year_page(page, year)

            self.db.log('success', f'Year {year} completed',
                       {'year': year, 'entries_found': len(entries)})

            return entries

        except PlaywrightTimeout:
            self.db.log('error', f'Timeout loading year {year}', {'year': year})
            return []
        except Exception as e:
            self.db.log('error', f'Error scraping year {year}: {str(e)}',
                       {'year': year, 'error': str(e)})
            return []

    async def parse_year_page(self, page, year):
        """Parse entries from a year page"""
        entries = []

        # Extract entries using JavaScript
        extracted = await page.evaluate('''(year) => {
            const results = [];
            const transliterations = {
                'תשרי': 'teshre', 'חשון': 'cheshvan', 'כסלו': 'kislev',
                'טבת': 'teves', 'שבט': 'shevat', 'אדר ראשון': 'adar_1',
                'אדר שני': 'adar_2', 'אדר': 'adar', 'ניסן': 'nissan',
                'אייר': 'iyar', 'סיון': 'sivan', 'תמוז': 'tammuz',
                'אב': 'av', 'אלול': 'elul'
            };

            // Find all month sections
            const monthSections = document.querySelectorAll('[class*="month"], [data-month], h2, h3');

            let currentMonth = null;
            let entryCount = 0;

            monthSections.forEach(section => {
                const text = section.textContent.trim();

                // Check if this is a month header
                const isMonth = Object.keys(transliterations).some(m => text.includes(m));

                if (isMonth) {
                    currentMonth = Object.keys(transliterations).find(m => text.includes(m));
                    entryCount = 0;
                    return;
                }

                // Look for entry patterns
                if (currentMonth) {
                    // Entry indicators: numbered list, occasion patterns, etc.
                    const entryPattern = /^(\d+\.|\d+[\)\-])?\s*([א-ת"\'\s]+[\u0591-\u05C7\s]*)/;

                    if (entryPattern.test(text) && text.length > 5 && text.length < 200) {
                        entryCount++;

                        results.push({
                            hebrew_year: year,
                            hebrew_month: currentMonth,
                            hebrew_month_translit: transliterations[currentMonth] || currentMonth,
                            sequence: entryCount,
                            occasion_he: text,
                            entry_url: null  // Will be constructed
                        });
                    }
                }
            });

            return results;
        }''', year)

        # Also try to find links in the page
        links = await page.evaluate('''() => {
            const links = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.getAttribute('href');
                if (href && (href.includes('/sichos/') || href.includes('/maamarim/') ||
                            href.includes('/likutei_'))) {
                    links.push({
                        url: href,
                        text: a.textContent.trim()
                    });
                }
            });
            return links;
        }''')

        # Build entry URLs from links
        for link in links:
            url = link['url']
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)

            # Parse URL: /sichos/5711/teshre/1
            match = re.match(r'/(\w+)/(\d+)/(\w+)/(\d+)', url)
            if match:
                category, year_num, month, seq = match.groups()

                entry = {
                    'hebrew_year': int(year_num),
                    'category': category,
                    'hebrew_month_translit': month,
                    'sequence': int(seq),
                    'entry_url': url,
                    'page_url': url,
                    'title': link['text'] or f'{category} {year_num}/{month}/{seq}',
                    'processing_status': 'discovered'
                }

                # Look up Hebrew month name
                for heb, trans in self.month_translit.items():
                    if trans == month:
                        entry['hebrew_month'] = heb
                        break

                entries.append(entry)

        # Store in database
        count = 0
        for entry in extracted + entries:
            entry_id = self.db.insert_entry(entry)
            if entry_id:
                count += 1

        print(f"  Found {count} entries")
        return entries

    async def scrape_entry_details(self, entry_url, page):
        """Scrape detailed content from an entry page"""
        try:
            await page.goto(entry_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)

            # Extract content using JavaScript
            details = await page.evaluate('''() => {
                const result = {
                    title: null,
                    description: null,
                    hebrew_content: null,
                    pdf_url: null,
                    audio_url: null,
                    video_url: null,
                    sources: []
                };

                // Try various selectors for title
                const titleSelectors = ['h1', 'h2', '.title', '[class*="title"]', '.entry-title'];
                for (const selector of titleSelectors) {
                    const el = document.querySelector(selector);
                    if (el && el.textContent.trim()) {
                        result.title = el.textContent.trim();
                        break;
                    }
                }

                // Description
                const descSelectors = ['.description', '.summary', '[class*="description"]', 'p'];
                for (const selector of descSelectors) {
                    const el = document.querySelector(selector);
                    if (el && el.textContent.trim() && el.textContent.trim().length > 20) {
                        result.description = el.textContent.trim();
                        break;
                    }
                }

                // Hebrew content
                const contentSelectors = ['.content', '[class*="content"]', '.text', 'article'];
                for (const selector of contentSelectors) {
                    const el = document.querySelector(selector);
                    if (el && el.textContent.trim()) {
                        result.hebrew_content = el.textContent.trim().substring(0, 10000);
                        break;
                    }
                }

                // PDF links
                document.querySelectorAll('a[href]').forEach(a => {
                    const href = a.getAttribute('href');
                    const text = a.textContent.trim().toLowerCase();

                    if (href && (href.includes('.pdf') || text.includes('pdf'))) {
                        result.sources.push({
                            type: 'pdf',
                            url: href,
                            title: a.textContent.trim() || 'PDF'
                        });
                    } else if (href && (href.includes('audio') || href.includes('mp3') || text.includes('audio'))) {
                        result.sources.push({
                            type: 'audio',
                            url: href,
                            title: a.textContent.trim() || 'Audio'
                        });
                    } else if (href && (href.includes('video') || href.includes('mp4') || text.includes('video'))) {
                        result.sources.push({
                            type: 'video',
                            url: href,
                            title: a.textContent.trim() || 'Video'
                        });
                    }
                });

                return result;
            }''')

            return details

        except Exception as e:
            self.db.log('error', f'Error scraping entry {entry_url}: {str(e)}',
                       {'url': entry_url, 'error': str(e)})
            return None

    async def scrape_all(self):
        """Main scraping routine - scrape all years"""
        start_time = datetime.now()

        print(f"{'='*70}")
        print(f"Mafteiach.app Scraper")
        print(f"{'='*70}")
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Years to scrape: {len(self.years)}")
        print(f"Database: {self.db.db_path}")
        print(f"{'='*70}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            # Set viewport and user agent
            await page.set_viewport_size({'width': 1920, 'height': 1080})
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            total_entries = 0

            for year in self.years:
                entries = await self.scrape_year(year, page)
                total_entries += len(entries)

                # Be respectful - add delay between requests
                await asyncio.sleep(2)

                # Print progress
                stats = self.db.get_stats()
                print(f"\nProgress: {stats['total_entries']} total entries in database")

            await browser.close()

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
            else:
                print(f"  {key}: {value}")

        return stats

    async def fetch_pending_content(self):
        """Fetch detailed content for entries that haven't been fetched yet"""
        pending = self.db.conn.execute('''
            SELECT id, entry_url, page_url FROM entries
            WHERE content_fetched = 0 AND (entry_url IS NOT NULL OR page_url IS NOT NULL)
            LIMIT 100
        ''').fetchall()

        if not pending:
            print("No pending entries to fetch")
            return

        print(f"Fetching content for {len(pending)} entries...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            for entry in pending:
                entry_id = entry['id']
                url = entry['page_url'] or entry['entry_url']

                if not url:
                    continue

                details = await self.scrape_entry_details(url, page)

                if details:
                    # Update entry with fetched content
                    self.db.conn.execute('''
                        UPDATE entries SET
                            title = COALESCE(?, title),
                            description = COALESCE(?, description),
                            hebrew_content = COALESCE(?, hebrew_content),
                            pdf_url = COALESCE(?, pdf_url),
                            audio_url = COALESCE(?, audio_url),
                            video_url = COALESCE(?, video_url),
                            content_fetched = 1,
                            processing_status = 'completed',
                            last_updated = ?
                        WHERE id = ?
                    ''', (
                        details.get('title'),
                        details.get('description'),
                        details.get('hebrew_content'),
                        details.get('pdf_url'),
                        details.get('audio_url'),
                        details.get('video_url'),
                        datetime.now().isoformat(),
                        entry_id
                    ))

                    # Store sources
                    if details.get('sources'):
                        for source in details['sources']:
                            self.db.insert_source({
                                'entry_id': entry_id,
                                'source_type': source['type'],
                                'url': source['url'],
                                'title': source.get('title'),
                                'downloaded': 0
                            })

                    self.db.conn.commit()

                await asyncio.sleep(1)

            await browser.close()

        print(f"Content fetch complete!")


async def main():
    """Main entry point"""
    import sys

    headless = '--headless' not in sys.argv

    scraper = MafteiachScraper(headless=headless)

    # Scrape all years
    await scraper.scrape_all()

    # Optionally fetch detailed content
    # await scraper.fetch_pending_content()

    # Export data
    print("\nExporting data...")
    json_path = scraper.db.export_json('mafteiach_export.json')
    csv_path = scraper.db.export_csv('mafteiach_export.csv')

    print(f"\nExported to:")
    print(f"  JSON: {json_path}")
    print(f"  CSV: {csv_path}")

    scraper.db.close()


if __name__ == '__main__':
    asyncio.run(main())
