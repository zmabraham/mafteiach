# Mafteiach - The Rebbe's Torah Index

A complete index of the Lubavitcher Rebbe's Torah teachings, covering 62 years from **תר"צ (1950)** through **תשנ"ב (1992)**.

## 📊 Overview

This project contains **3,350 entries** documenting the Rebbe's Torah, including:

- **Sichos** (Talks)
- **Maamarim** (Chassidic Discourses)
- **Likutei Sichos** (Collected Talks)
- **Farbrengens** (Gatherings)

## 🌐 Live Demo

Visit the live site: [https://zmabraham.github.io/mafteiach/](https://zmabraham.github.io/mafteiach/)

## 📁 Data Source

Data is sourced from [mafteiach.app](https://www.mafteiach.app), which maintains a comprehensive digital index of the Lubavitcher Rebbe's Torah.

## 🚀 Features

- **Complete Database**: 3,350 entries spanning 62 years
- **Full-Text Search**: Search in Hebrew and English
- **Filter by Year**: Browse specific years
- **Direct Links**: Each entry links to the original source
- **GitHub Pages**: Static site for fast loading
- **Responsive Design**: Works on desktop and mobile

## 📅 Year Coverage

| Hebrew Year | Gregorian | Entries |
|-------------|-----------|---------|
| תר"צ (5690) | 1929-1930 | Early period |
| תש"י (5710) | 1949-1950 | 36 |
| תשי"א (5711) | 1950-1951 | 85 |
| תשנ"ט (5749) | 1988-1989 | 176 |
| תשנ"ב (5752) | 1991-1992 | 82 |

## 🛠️ Development

### Prerequisites

```bash
pip install -r requirements.txt
```

### Generate Frontend

```bash
python generate_frontend.py
```

This creates a self-contained `frontend/index.html` with embedded data.

### Run API Server (Local)

```bash
python api.py
```

Then visit http://localhost:8000 for interactive API.

## 📦 Project Structure

```
mafteiach/
├── frontend/           # GitHub Pages site
│   └── index.html     # Self-contained with embedded data
├── mafteiach.db       # SQLite database
├── api.py             # FastAPI server (optional)
├── direct_scraper.py  # Data scraper
├── db_setup.py        # Database schema
└── README.md          # This file
```

## 🤝 Contributing

This is a reference implementation. Contributions welcome:

- Additional metadata extraction
- Improved search functionality
- Better Hebrew calendar integration
- Source content extraction

## 📄 License

Data sourced from mafteiach.app. Please refer to their terms of use.

## 📞 Contact

- Original Data: [mafteiach.app](https://www.mafteiach.app)
- Issues: [GitHub Issues](https://github.com/zmabraham/mafteiach/issues)

## ⚡ Kudos

- Inspired by the comprehensive index at mafteiach.app
- Built to preserve and make accessible the Rebbe's Torah
- May the merit of the Rebbe protect us all

---

**לעילוי נשמת** - For the elevation of the soul
