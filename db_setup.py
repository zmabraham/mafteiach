#!/usr/bin/env python3
"""
Mafteiach.app Database Setup
Creates SQLite database with schema for storing all entries
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

class MafteiachDatabase:
    def __init__(self, db_path='mafteiach.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.insert_static_data()

    def create_tables(self):
        """Create all database tables"""

        # Main entries table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Hebrew Calendar
                hebrew_year INTEGER,
                hebrew_month TEXT,
                hebrew_month_translit TEXT,
                hebrew_day INTEGER,

                -- Gregorian Calendar (calculated)
                gregorian_year INTEGER,
                gregorian_date TEXT,

                -- Entry Metadata
                category TEXT,
                subcategory TEXT,
                sequence INTEGER,

                -- Occasion data
                occasion_he TEXT,
                occasion_en TEXT,
                detail TEXT,
                parsha TEXT,

                -- URLs
                entry_url TEXT UNIQUE,
                page_url TEXT,

                -- Content
                title TEXT,
                description TEXT,
                hebrew_content TEXT,

                -- Links
                pdf_url TEXT,
                audio_url TEXT,
                video_url TEXT,

                -- Timestamps
                scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT,

                -- Processing flags
                content_fetched BOOLEAN DEFAULT 0,
                sources_extracted BOOLEAN DEFAULT 0,
                processing_status TEXT DEFAULT 'pending'
            )
        ''')

        # Sources table (PDFs, audio files, etc.)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE,
                source_type TEXT,
                url TEXT UNIQUE,
                title TEXT,
                description TEXT,
                language TEXT,
                file_size INTEGER,
                downloaded BOOLEAN DEFAULT 0,
                local_path TEXT,
                checksum TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Cross-references table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS cross_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER REFERENCES entries(id) ON DELETE CASCADE,
                ref_type TEXT,
                ref_value TEXT,
                ref_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Scraping log
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS scraping_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_type TEXT,
                message TEXT,
                details TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_hebrew_year ON entries(hebrew_year)',
            'CREATE INDEX IF NOT EXISTS idx_category ON entries(category)',
            'CREATE INDEX IF NOT EXISTS idx_parsha ON entries(parsha)',
            'CREATE INDEX IF NOT EXISTS idx_month_year ON entries(hebrew_year, hebrew_month)',
            'CREATE INDEX IF NOT EXISTS idx_gregorian_date ON entries(gregorian_date)',
            'CREATE INDEX IF NOT EXISTS idx_entry_url ON entries(entry_url)',
            'CREATE INDEX IF NOT EXISTS idx_sources_entry ON sources(entry_id)',
            'CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type)',
            'CREATE INDEX IF NOT EXISTS idx_xref_entry ON cross_references(entry_id)',
            'CREATE INDEX IF NOT EXISTS idx_xref_type ON cross_references(ref_type)',
            'CREATE INDEX IF NOT EXISTS idx_scrape_status ON entries(processing_status)',
            'CREATE INDEX IF NOT EXISTS idx_log_type ON scraping_log(log_type)',
            'CREATE INDEX IF NOT EXISTS idx_log_timestamp ON scraping_log(timestamp)',
        ]

        for idx in indexes:
            self.conn.execute(idx)

        # Full-text search table
        self.conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
                title, description, hebrew_content,
                occasion_he, detail, parsha,
                content='entries',
                content_rowid='id'
            )
        ''')

        # FTS triggers
        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
                INSERT INTO entries_fts(rowid, title, description, hebrew_content, occasion_he, detail, parsha)
                VALUES (new.id, new.title, new.description, new.hebrew_content, new.occasion_he, new.detail, new.parsha);
            END
        ''')

        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
                DELETE FROM entries_fts WHERE rowid = old.id;
            END
        ''')

        self.conn.commit()

    def insert_static_data(self):
        """Insert static reference data"""

        # Hebrew months mapping
        months = [
            ('תשרי', 'teshre', 'Tishrei', 7),
            ('חשון', 'cheshvan', 'Cheshvan', 8),
            ('כסלו', 'kislev', 'Kislev', 9),
            ('טבת', 'teves', 'Teves', 10),
            ('שבט', 'shevat', 'Shevat', 11),
            ('אדר ראשון', 'adar_1', 'Adar I', 12),
            ('אדר שני', 'adar_2', 'Adar II', 13),
            ('אדר', 'adar', 'Adar', 12),
            ('ניסן', 'nissan', 'Nissan', 1),
            ('אייר', 'iyar', 'Iyar', 2),
            ('סיון', 'sivan', 'Sivan', 3),
            ('תמוז', 'tammuz', 'Tammuz', 4),
            ('אב', 'av', 'Av', 5),
            ('אלול', 'elul', 'Elul', 6),
        ]

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS hebrew_months (
                hebrew TEXT PRIMARY KEY,
                transliteration TEXT UNIQUE,
                english TEXT,
                gregorian_month INTEGER
            )
        ''')

        for m in months:
            self.conn.execute('''
                INSERT OR IGNORE INTO hebrew_months VALUES (?,?,?,?)
            ''', m)

        # Categories
        categories = [
            ('sichos', 'שיחות', 'Talks'),
            ('maamarim', 'מאמרים', 'Discourses'),
            ('maamarim_meluket', 'מאמרים מלוקט', 'Selected Discourses'),
            ('likutei_sichos', 'לקוטי שיחות', 'Collected Talks'),
            ('michtavim', 'מכתבים', 'Letters'),
            ('klalim_yomanim', 'כללים יומנים', 'Daily Rules'),
        ]

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                slug TEXT PRIMARY KEY,
                hebrew TEXT,
                english TEXT
            )
        ''')

        for c in categories:
            self.conn.execute('''
                INSERT OR IGNORE INTO categories VALUES (?,?,?)
            ''', c)

        self.conn.commit()

    def log(self, log_type, message, details=None):
        """Log scraping activity"""
        self.conn.execute('''
            INSERT INTO scraping_log (log_type, message, details)
            VALUES (?, ?, ?)
        ''', (log_type, message, json.dumps(details) if details else None))
        self.conn.commit()

    def insert_entry(self, entry_data):
        """Insert or update an entry"""
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO entries (
                    hebrew_year, hebrew_month, hebrew_month_translit,
                    hebrew_day, gregorian_year, gregorian_date,
                    category, subcategory, sequence,
                    occasion_he, occasion_en, detail, parsha,
                    entry_url, page_url,
                    title, description, hebrew_content,
                    pdf_url, audio_url, video_url,
                    content_fetched, sources_extracted, processing_status
                ) VALUES (
                    :hebrew_year, :hebrew_month, :hebrew_month_translit,
                    :hebrew_day, :gregorian_year, :gregorian_date,
                    :category, :subcategory, :sequence,
                    :occasion_he, :occasion_en, :detail, :parsha,
                    :entry_url, :page_url,
                    :title, :description, :hebrew_content,
                    :pdf_url, :audio_url, :video_url,
                    :content_fetched, :sources_extracted, :processing_status
                )
            ''', entry_data)
            self.conn.commit()
            return self.conn.lastrowid
        except sqlite3.IntegrityError as e:
            self.log('error', f'Duplicate entry URL: {entry_data.get("entry_url")}', {'error': str(e)})
            return None

    def insert_source(self, source_data):
        """Insert or update a source"""
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO sources (
                    entry_id, source_type, url, title, description,
                    language, file_size, downloaded, local_path, checksum, metadata
                ) VALUES (
                    :entry_id, :source_type, :url, :title, :description,
                    :language, :file_size, :downloaded, :local_path, :checksum, :metadata
                )
            ''', source_data)
            self.conn.commit()
            return self.conn.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_entries_by_year(self, year):
        """Get all entries for a Hebrew year"""
        return self.conn.execute('''
            SELECT * FROM entries WHERE hebrew_year = ?
            ORDER BY hebrew_month, sequence
        ''', (year,)).fetchall()

    def get_entry_by_url(self, url):
        """Get an entry by its URL"""
        return self.conn.execute('''
            SELECT * FROM entries WHERE entry_url = ?
        ''', (url,)).fetchone()

    def get_stats(self):
        """Get database statistics"""
        stats = {}

        stats['total_entries'] = self.conn.execute(
            'SELECT COUNT(*) FROM entries'
        ).fetchone()[0]

        stats['entries_by_year'] = dict(self.conn.execute('''
            SELECT hebrew_year, COUNT(*) FROM entries
            GROUP BY hebrew_year ORDER BY hebrew_year
        ''').fetchall())

        stats['entries_by_category'] = dict(self.conn.execute('''
            SELECT category, COUNT(*) FROM entries
            WHERE category IS NOT NULL
            GROUP BY category
        ''').fetchall())

        stats['total_sources'] = self.conn.execute(
            'SELECT COUNT(*) FROM sources'
        ).fetchone()[0]

        stats['sources_by_type'] = dict(self.conn.execute('''
            SELECT source_type, COUNT(*) FROM sources
            GROUP BY source_type
        ''').fetchall())

        stats['pending_content'] = self.conn.execute('''
            SELECT COUNT(*) FROM entries WHERE content_fetched = 0
        ''').fetchone()[0]

        return stats

    def export_json(self, output_path='mafteiach_export.json'):
        """Export entire database to JSON"""
        data = {
            'export_date': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'entries': []
        }

        entries = self.conn.execute('''
            SELECT e.*,
                   GROUP_CONCAT(DISTINCT s.url) as source_urls
            FROM entries e
            LEFT JOIN sources s ON s.entry_id = e.id
            GROUP BY e.id
            ORDER BY e.hebrew_year, e.hebrew_month, e.sequence
        ''').fetchall()

        for entry in entries:
            entry_dict = dict(entry)
            # Remove None values
            entry_dict = {k: v for k, v in entry_dict.items() if v is not None}
            data['entries'].append(entry_dict)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_path

    def export_csv(self, output_path='mafteiach_export.csv'):
        """Export entries to CSV"""
        import csv

        entries = self.conn.execute('''
            SELECT * FROM entries ORDER BY hebrew_year, hebrew_month, sequence
        ''').fetchall()

        if not entries:
            return None

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=entries[0].keys())
            writer.writeheader()
            writer.writerows([dict(e) for e in entries])

        return output_path

    def close(self):
        """Close database connection"""
        self.conn.close()


if __name__ == '__main__':
    # Create database
    db = MafteiachDatabase('mafteiach.db')
    print("Database created successfully!")
    print(f"Database location: {Path('mafteiach.db').absolute()}")
    print(f"\nInitial stats: {db.get_stats()}")
