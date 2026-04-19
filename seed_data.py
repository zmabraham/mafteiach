#!/usr/bin/env python3
"""
Seed mafteiach database with sample data from year 5711 (תשי"א)
Based on analysis from mafteiach.app
"""

from db_setup import MafteiachDatabase
import json

# Sample data from year 5711 (תשי"א / 1950-1951)
sample_entries = [
    # תשרי (Tishrei) - 10 entries
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'hebrew_day': None,
        'gregorian_year': 1950,
        'gregorian_date': None,
        'sequence': 1,
        'category': 'sichos',
        'subcategory': None,
        'occasion_he': 'יום א׳ דר״ה, בעת ההליכה לתשליך',
        'occasion_en': 'Sunday before Rosh Hashana, during the Tashlich walk',
        'detail': 'First day of Rosh Hashana',
        'parsha': None,
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/1',
        'title': 'יום א׳ דר״ה - תשליך',
        'description': 'Sunday before Rosh Hashana',
        'hebrew_content': None,
        'pdf_url': None,
        'audio_url': None,
        'video_url': None,
        'content_fetched': 0,
        'sources_extracted': 0,
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 2,
        'occasion_he': 'ערב יו״כ, בעת נתינת לקח',
        'occasion_en': 'Erev Yom Kippur, during the giving of the Machzor',
        'detail': 'Erev Yom Kippur',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/2',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/2',
        'category': 'sichos',
        'title': 'ערב יו״כ - נתינת לקח',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 3,
        'occasion_he': 'ערב יו״כ, ברכה לפני כל נדרי',
        'occasion_en': 'Erev Yom Kippur, blessing before Kol Nidrei',
        'detail': 'Erev Yom Kippur',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/3',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/3',
        'category': 'sichos',
        'title': 'ערב יו״כ - כל נדרי',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 4,
        'occasion_he': 'מוצאי יו״כ, בעת הסעודה',
        'occasion_en': 'Motzai Yom Kippur, during the meal',
        'detail': 'Motzai Yom Kippur',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/4',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/4',
        'category': 'sichos',
        'title': 'מוצאי יו״כ',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 5,
        'occasion_he': 'מוצאי יום ג׳ דחה״ס, א׳ דחוה״מ, שמב״ה',
        'occasion_en': 'Tuesday night, Wednesday of Chol Hamoed, Shabbos Mevorchim',
        'detail': 'Chol Hamoed Sukkos',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/5',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/5',
        'category': 'sichos',
        'title': 'חוה״מ סוכות - שמב״ה',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 6,
        'occasion_he': 'שבת חוה״מ סוכות',
        'occasion_en': 'Shabbos Chol Hamoed Sukkos',
        'detail': 'Shabbos Chol Hamoed Sukkos',
        'parsha': 'תשולח',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/6',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/6',
        'category': 'sichos',
        'title': 'שבת חוה״מ סוכות',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 7,
        'occasion_he': 'ליל שמח״ת, לפני הקפות',
        'occasion_en': 'Eve of Simchas Torah, before Hakafos',
        'detail': 'Simchas Torah Eve',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/7',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/7',
        'category': 'sichos',
        'title': 'ליל שמח״ת',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 8,
        'occasion_he': 'יום שמח״ת',
        'occasion_en': 'Simchas Torah Day',
        'detail': 'Simchas Torah',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/8',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/8',
        'category': 'sichos',
        'title': 'יום שמח״ת',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 9,
        'occasion_he': 'כ״ד תשרי, אסרו חג',
        'occasion_en': '24 Tishrei, Isru Chag',
        'detail': 'Isru Chag Sukkos',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/9',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/9',
        'category': 'sichos',
        'title': 'אסרו חג',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תשרי',
        'hebrew_month_translit': 'teshre',
        'sequence': 10,
        'occasion_he': 'בראשית, מבה״ח מ״ח',
        'occasion_en': 'Parshas Bereishis, Moadim v\'Chagim Marcheshvan',
        'detail': 'Shabbos Bereishis',
        'parsha': 'בראשית',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teshre/10',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teshre/10',
        'category': 'sichos',
        'title': 'שבת בראשית',
        'processing_status': 'completed'
    },
    # חשון (Cheshvan) - 2 entries
    {
        'hebrew_year': 5711,
        'hebrew_month': 'חשון',
        'hebrew_month_translit': 'cheshvan',
        'sequence': 1,
        'occasion_he': 'לך לך, יו״ד מ״ח',
        'occasion_en': 'Parshas Lech Lecha, Thursday Marcheshvan',
        'detail': 'Thursday',
        'parsha': 'לך לך',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/cheshvan/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/cheshvan/1',
        'category': 'sichos',
        'title': 'לך לך',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'חשון',
        'hebrew_month_translit': 'cheshvan',
        'sequence': 2,
        'occasion_he': 'חיי שרה, מבה״ח כסלו',
        'occasion_en': 'Parshas Chayei Sarah, Moadim v\'Chagim Kislev',
        'detail': 'Shabbos Chayei Sarah',
        'parsha': 'חיי שרה',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/cheshvan/2',
        'page_url': 'https://www.mafteiach.app/sichos/5711/cheshvan/2',
        'category': 'sichos',
        'title': 'שבת חיי שרה',
        'processing_status': 'completed'
    },
    # כסלו (Kislev) - 3 entries
    {
        'hebrew_year': 5711,
        'hebrew_month': 'כסלו',
        'hebrew_month_translit': 'kislev',
        'sequence': 1,
        'occasion_he': 'ויצא, ט׳ כסלו',
        'occasion_en': 'Parshas Vayeitzei, 9 Kislev',
        'detail': '9 Kislev',
        'parsha': 'ויצא',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/kislev/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/kislev/1',
        'category': 'sichos',
        'title': 'ט׳ כסלו - יארצייט',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'כסלו',
        'hebrew_month_translit': 'kislev',
        'sequence': 2,
        'occasion_he': 'י״ט כסלו',
        'occasion_en': '19 Kislev',
        'detail': '19 Kislev - Release of the Alter Rebbe',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/kislev/2',
        'page_url': 'https://www.mafteiach.app/sichos/5711/kislev/2',
        'category': 'sichos',
        'title': 'י״ט כסלו',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'כסלו',
        'hebrew_month_translit': 'kislev',
        'sequence': 3,
        'occasion_he': 'וישב, מבה״ח טבת',
        'occasion_en': 'Parshas Vayishlach, Moadim v\'Chagim Teves',
        'detail': 'Shabbos Vayishlach',
        'parsha': 'וישב',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/kislev/3',
        'page_url': 'https://www.mafteiach.app/sichos/5711/kislev/3',
        'category': 'sichos',
        'title': 'שבת וישב',
        'processing_status': 'completed'
    },
    # Additional sample entries for other months
    {
        'hebrew_year': 5711,
        'hebrew_month': 'טבת',
        'hebrew_month_translit': 'teves',
        'sequence': 1,
        'occasion_he': 'י׳ טבת',
        'occasion_en': '10 Teves',
        'detail': 'Asarah B\'Teves',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/teves/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/teves/1',
        'category': 'sichos',
        'title': 'י׳ טבת',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'שבט',
        'hebrew_month_translit': 'shevat',
        'sequence': 1,
        'occasion_he': 'ט׳ שבט',
        'occasion_en': '15 Shevat',
        'detail': 'Tu B\'Shevat',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/shevat/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/shevat/1',
        'category': 'sichos',
        'title': 'ט׳ שבט',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'אדר',
        'hebrew_month_translit': 'adar',
        'sequence': 1,
        'occasion_he': 'פרשת זכור',
        'occasion_en': 'Parshas Zachor',
        'detail': 'Shabbos Zachor',
        'parsha': 'זכור',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/adar/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/adar/1',
        'category': 'sichos',
        'title': 'שבת פרשת זכור',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'ניסן',
        'hebrew_month_translit': 'nissan',
        'sequence': 1,
        'occasion_he': 'שבת הגדול',
        'occasion_en': 'Shabbos HaGadol',
        'detail': 'Shabbos before Pesach',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/nissan/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/nissan/1',
        'category': 'sichos',
        'title': 'שבת הגדול',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'ניסן',
        'hebrew_month_translit': 'nissan',
        'sequence': 2,
        'occasion_he': 'ערב פסח',
        'occasion_en': 'Erev Pesach',
        'detail': 'Erev Pesach',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/nissan/2',
        'page_url': 'https://www.mafteiach.app/sichos/5711/nissan/2',
        'category': 'sichos',
        'title': 'ערב פסח',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'אייר',
        'hebrew_month_translit': 'iyar',
        'sequence': 1,
        'occasion_he': 'ל״ג בעומר',
        'occasion_en': 'Lag BaOmer',
        'detail': '33rd day of Omer',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/iyar/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/iyar/1',
        'category': 'sichos',
        'title': 'ל״ג בעומר',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'סיון',
        'hebrew_month_translit': 'sivan',
        'sequence': 1,
        'occasion_he': 'שבועות',
        'occasion_en': 'Shavuos',
        'detail': 'Yom Tov Shavuos',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/sivan/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/sivan/1',
        'category': 'sichos',
        'title': 'שבועות',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'תמוז',
        'hebrew_month_translit': 'tammuz',
        'sequence': 1,
        'occasion_he': 'י״ז בתמוז - יארצייט',
        'occasion_en': '17 Tammuz - Yahrtzeit',
        'detail': 'Fast of 17 Tammuz',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/tammuz/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/tammuz/1',
        'category': 'sichos',
        'title': 'י״ז בתמוז',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'אב',
        'hebrew_month_translit': 'av',
        'sequence': 1,
        'occasion_he': 'תשעה באב',
        'occasion_en': 'Tisha B\'Av',
        'detail': 'Fast of 9 Av',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/av/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/av/1',
        'category': 'sichos',
        'title': 'תשעה באב',
        'processing_status': 'completed'
    },
    {
        'hebrew_year': 5711,
        'hebrew_month': 'אלול',
        'hebrew_month_translit': 'elul',
        'sequence': 1,
        'occasion_he': 'שבת ראש חודש אלול',
        'occasion_en': 'Shabbos Rosh Chodesh Elul',
        'detail': 'Rosh Chodesh Elul',
        'entry_url': 'https://www.mafteiach.app/sichos/5711/elul/1',
        'page_url': 'https://www.mafteiach.app/sichos/5711/elul/1',
        'category': 'sichos',
        'title': 'ראש חודש אלול',
        'processing_status': 'completed'
    },
]


def seed_database():
    """Seed database with sample entries"""
    db = MafteiachDatabase('mafteiach.db')

    print("Seeding database with sample data from year 5711...")
    print("=" * 60)

    count = 0
    for entry in sample_entries:
        entry_id = db.insert_entry(entry)
        if entry_id:
            count += 1
            print(f"✓ Added: {entry['hebrew_month']} - {entry['occasion_he'][:40]}")

    # Add some sample sources
    print("\nAdding sample source links...")
    sources = [
        {
            'entry_id': 1,
            'source_type': 'pdf',
            'url': 'https://example.com/sichos/5711/teshre/1.pdf',
            'title': 'Sicha - Yom Alef Rosh Hashana',
            'language': 'hebrew',
            'downloaded': 0
        },
        {
            'entry_id': 1,
            'source_type': 'audio',
            'url': 'https://example.com/audio/5711/teshre/1.mp3',
            'title': 'Audio - Sicha',
            'language': 'hebrew',
            'downloaded': 0
        },
    ]

    for source in sources:
        source_id = db.insert_source(source)
        if source_id:
            print(f"✓ Added source: {source['source_type']}")

    # Get stats
    stats = db.get_stats()

    print("\n" + "=" * 60)
    print(f"Database seeded successfully!")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Total sources: {stats['total_sources']}")

    # Export
    print("\nExporting data...")
    json_path = db.export_json('mafteiach_export.json')
    csv_path = db.export_csv('mafteiach_export.csv')

    print(f"\nExported to:")
    print(f"  JSON: {json_path}")
    print(f"  CSV: {csv_path}")

    db.close()

    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. View data: sqlite3 mafteiach.db 'SELECT * FROM entries LIMIT 5'")
    print("2. Start API: python api.py")
    print("3. Open web interface: web_interface.html")
    print("=" * 60)


if __name__ == '__main__':
    seed_database()
