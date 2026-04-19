#!/usr/bin/env python3
"""
Quick seed for mafteiach database with sample entries
"""

import sqlite3
from pathlib import Path

DB_PATH = 'mafteiach.db'

# Sample entries from year 5711
entries_data = [
    # Tishrei
    (5711, 'תשרי', 'teshre', None, 1950, None, 'sichos', None, 1,
     'יום א׳ דר״ה, בעת ההליכה לתשליך', 'Sunday before Rosh Hashana', 'Tashlich walk', None,
     'https://www.mafteiach.app/sichos/5711/teshre/1', 'https://www.mafteiach.app/sichos/5711/teshre/1',
     'יום א׳ דר״ה', 'Sunday before RH', None, None, None, None, 0, 0, 'completed'),
    (5711, 'תשרי', 'teshre', None, 1950, None, 'sichos', None, 2,
     'ערב יו״כ', 'Erev Yom Kippur', 'Erev YK', None,
     'https://www.mafteiach.app/sichos/5711/teshre/2', 'https://www.mafteiach.app/sichos/5711/teshre/2',
     'ערב יו״כ', 'Erev YK', None, None, None, None, 0, 0, 'completed'),
    (5711, 'תשרי', 'teshre', None, 1950, None, 'sichos', None, 3,
     'מוצאי יו״כ', 'Motzai Yom Kippur', 'After YK', None,
     'https://www.mafteiach.app/sichos/5711/teshre/3', 'https://www.mafteiach.app/sichos/5711/teshre/3',
     'מוצאי יו״כ', 'Motzai YK', None, None, None, None, 0, 0, 'completed'),
    (5711, 'תשרי', 'teshre', None, 1950, None, 'sichos', None, 4,
     'שבת חוה״מ סוכות', 'Shabbos Chol Hamoed Sukkos', 'Chol Hamoed', 'תשולח',
     'https://www.mafteiach.app/sichos/5711/teshre/4', 'https://www.mafteiach.app/sichos/5711/teshre/4',
     'שבת חוה״מ סוכות', 'Shabbos Chol Hamoed', None, None, None, None, 0, 0, 'completed'),
    (5711, 'תשרי', 'teshre', None, 1950, None, 'sichos', None, 5,
     'יום שמח״ת', 'Simchas Torah', 'Simchas Torah', None,
     'https://www.mafteiach.app/sichos/5711/teshre/5', 'https://www.mafteiach.app/sichos/5711/teshre/5',
     'יום שמח״ת', 'Simchas Torah', None, None, None, None, 0, 0, 'completed'),
    (5711, 'תשרי', 'teshre', None, 1950, None, 'sichos', None, 6,
     'בראשית', 'Parshas Bereishis', 'Shabbos Bereishis', 'בראשית',
     'https://www.mafteiach.app/sichos/5711/teshre/6', 'https://www.mafteiach.app/sichos/5711/teshre/6',
     'שבת בראשית', 'Shabbos Bereishis', None, None, None, None, 0, 0, 'completed'),
    # Cheshvan
    (5711, 'חשון', 'cheshvan', None, 1950, None, 'sichos', None, 1,
     'לך לך', 'Parshas Lech Lecha', 'Thursday', 'לך לך',
     'https://www.mafteiach.app/sichos/5711/cheshvan/1', 'https://www.mafteiach.app/sichos/5711/cheshvan/1',
     'לך לך', 'Lech Lecha', None, None, None, None, 0, 0, 'completed'),
    (5711, 'חשון', 'cheshvan', None, 1950, None, 'sichos', None, 2,
     'חיי שרה', 'Parshas Chayei Sarah', 'Shabbos', 'חיי שרה',
     'https://www.mafteiach.app/sichos/5711/cheshvan/2', 'https://www.mafteiach.app/sichos/5711/cheshvan/2',
     'חיי שרה', 'Chayei Sarah', None, None, None, None, 0, 0, 'completed'),
    # Kislev
    (5711, 'כסלו', 'kislev', None, 1950, None, 'sichos', None, 1,
     'י״ט כסלו', '19 Kislev', 'Yud Tes Kislev', None,
     'https://www.mafteiach.app/sichos/5711/kislev/1', 'https://www.mafteiach.app/sichos/5711/kislev/1',
     'י״ט כסלו', '19 Kislev', None, None, None, None, 0, 0, 'completed'),
    # Teves
    (5711, 'טבת', 'teves', None, 1951, None, 'sichos', None, 1,
     'י׳ טבת', '10 Teves', 'Asara B\'Teves', None,
     'https://www.mafteiach.app/sichos/5711/teves/1', 'https://www.mafteiach.app/sichos/5711/teves/1',
     'י׳ טבת', '10 Teves', None, None, None, None, 0, 0, 'completed'),
    # Shevat
    (5711, 'שבט', 'shevat', None, 1951, None, 'sichos', None, 1,
     'ט׳ שבט', '15 Shevat', 'Tu B\'Shevat', None,
     'https://www.mafteiach.app/sichos/5711/shevat/1', 'https://www.mafteiach.app/sichos/5711/shevat/1',
     'ט׳ שבט', '15 Shevat', None, None, None, None, 0, 0, 'completed'),
    # Adar
    (5711, 'אדר', 'adar', None, 1951, None, 'sichos', None, 1,
     'פרשת זכור', 'Parshas Zachor', 'Shabbos Zachor', 'זכור',
     'https://www.mafteiach.app/sichos/5711/adar/1', 'https://www.mafteiach.app/sichos/5711/adar/1',
     'פרשת זכור', 'Parshas Zachor', None, None, None, None, 0, 0, 'completed'),
    # Nissan
    (5711, 'ניסן', 'nissan', None, 1951, None, 'sichos', None, 1,
     'שבת הגדול', 'Shabbos HaGadol', 'Before Pesach', None,
     'https://www.mafteiach.app/sichos/5711/nissan/1', 'https://www.mafteiach.app/sichos/5711/nissan/1',
     'שבת הגדול', 'Shabbos HaGadol', None, None, None, None, 0, 0, 'completed'),
    (5711, 'ניסן', 'nissan', None, 1951, None, 'sichos', None, 2,
     'ערב פסח', 'Erev Pesach', 'Erev Pesach', None,
     'https://www.mafteiach.app/sichos/5711/nissan/2', 'https://www.mafteiach.app/sichos/5711/nissan/2',
     'ערב פסח', 'Erev Pesach', None, None, None, None, 0, 0, 'completed'),
    # Iyar
    (5711, 'אייר', 'iyar', None, 1951, None, 'sichos', None, 1,
     'ל״ג בעומר', 'Lag BaOmer', '33 Omer', None,
     'https://www.mafteiach.app/sichos/5711/iyar/1', 'https://www.mafteiach.app/sichos/5711/iyar/1',
     'ל״ג בעומר', 'Lag BaOmer', None, None, None, None, 0, 0, 'completed'),
    # Sivan
    (5711, 'סיון', 'sivan', None, 1951, None, 'sichos', None, 1,
     'שבועות', 'Shavuos', 'Yom Tov', None,
     'https://www.mafteiach.app/sichos/5711/sivan/1', 'https://www.mafteiach.app/sichos/5711/sivan/1',
     'שבועות', 'Shavuos', None, None, None, None, 0, 0, 'completed'),
    # Tammuz
    (5711, 'תמוז', 'tammuz', None, 1951, None, 'sichos', None, 1,
     'י״ז בתמוז', '17 Tammuz', 'Fast day', None,
     'https://www.mafteiach.app/sichos/5711/tammuz/1', 'https://www.mafteiach.app/sichos/5711/tammuz/1',
     'י״ז בתמוז', '17 Tammuz', None, None, None, None, 0, 0, 'completed'),
    # Av
    (5711, 'אב', 'av', None, 1951, None, 'sichos', None, 1,
     'תשעה באב', 'Tisha B\'Av', 'Fast day', None,
     'https://www.mafteiach.app/sichos/5711/av/1', 'https://www.mafteiach.app/sichos/5711/av/1',
     'תשעה באב', 'Tisha B\'Av', None, None, None, None, 0, 0, 'completed'),
    # Elul
    (5711, 'אלול', 'elul', None, 1951, None, 'sichos', None, 1,
     'ראש חודש אלול', 'Rosh Chodesh Elul', 'Start of Elul', None,
     'https://www.mafteiach.app/sichos/5711/elul/1', 'https://www.mafteiach.app/sichos/5711/elul/1',
     'ראש חודש אלול', 'Rosh Chodesh Elul', None, None, None, None, 0, 0, 'completed'),
]

def seed_database():
    """Seed database with sample entries"""
    if not Path(DB_PATH).exists():
        print(f"Database not found at {DB_PATH}")
        print("Run 'python db_setup.py' first")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Seeding database with sample entries from year 5711...")
    print("=" * 60)

    count = 0
    for entry in entries_data:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO entries (
                    hebrew_year, hebrew_month, hebrew_month_translit,
                    hebrew_day, gregorian_year, gregorian_date,
                    category, subcategory, sequence,
                    occasion_he, occasion_en, detail, parsha,
                    entry_url, page_url,
                    title, description, hebrew_content,
                    pdf_url, audio_url, video_url,
                    content_fetched, sources_extracted, processing_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', entry)
            count += 1
            heb = entry[9][:30]
            print(f"✓ Added: {entry[1]} - {heb}...")
        except sqlite3.IntegrityError as e:
            print(f"  Skipped duplicate: {entry[15]}")

    conn.commit()

    # Add sample sources
    print("\nAdding sample sources...")
    sources = [
        (1, 'pdf', 'https://example.com/sichos/5711/teshre/1.pdf', 'Sicha PDF', 'hebrew', 0, None, None, None),
        (1, 'audio', 'https://example.com/audio/5711/teshre/1.mp3', 'Audio recording', 'hebrew', 0, None, None, None),
        (4, 'pdf', 'https://example.com/sichos/5711/teshre/4.pdf', 'Shabbos Chol Hamoed PDF', 'hebrew', 0, None, None, None),
    ]

    for source in sources:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO sources (
                    entry_id, source_type, url, title, language, downloaded, local_path, checksum, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', source)
            print(f"✓ Added source: {source[1]}")
        except sqlite3.IntegrityError:
            pass

    conn.commit()

    # Get stats
    stats = cursor.execute('SELECT COUNT(*) FROM entries').fetchone()[0]
    sources_count = cursor.execute('SELECT COUNT(*) FROM sources').fetchone()[0]

    print("\n" + "=" * 60)
    print(f"Database seeded successfully!")
    print(f"Total entries: {stats}")
    print(f"Total sources: {sources_count}")

    # Sample queries
    print("\nSample data:")
    rows = cursor.execute('''
        SELECT hebrew_month, occasion_he, occasion_en
        FROM entries ORDER BY hebrew_month, sequence LIMIT 5
    ''').fetchall()

    for row in rows:
        print(f"  {row[0]}: {row[1][:40]}")

    conn.close()

    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Browse data: sqlite3 mafteiach.db 'SELECT * FROM entries LIMIT 5'")
    print("2. Start API: PYTHONPATH=/usr/local/lib/python3.11/dist-packages python3 api.py")
    print("3. Open web interface: Open web_interface.html in browser")
    print("=" * 60)


if __name__ == '__main__':
    seed_database()
