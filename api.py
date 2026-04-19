#!/usr/bin/env python3
"""
Mafteiach.app API Server
FastAPI server for querying the mafteiach database
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from pathlib import Path
import uvicorn

# Database path
DB_PATH = 'mafteiach.db'

app = FastAPI(
    title="Mafteiach.app API",
    description="API for the Lubavitcher Rebbe's Torah index",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Entry(BaseModel):
    id: int
    hebrew_year: Optional[int] = None
    hebrew_month: Optional[str] = None
    hebrew_month_translit: Optional[str] = None
    occasion_he: Optional[str] = None
    occasion_en: Optional[str] = None
    detail: Optional[str] = None
    parsha: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    entry_url: Optional[str] = None
    pdf_url: Optional[str] = None
    audio_url: Optional[str] = None


class Stats(BaseModel):
    total_entries: int
    entries_by_year: dict
    entries_by_category: dict
    total_sources: int
    sources_by_type: dict


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
async def root():
    """API root with documentation"""
    return {
        "name": "Mafteiach.app API",
        "version": "1.0.0",
        "endpoints": {
            "stats": "/api/stats",
            "entries": "/api/entries",
            "entry": "/api/entries/{id}",
            "search": "/api/search",
            "years": "/api/years",
            "parshas": "/api/parshas",
            "export": "/api/export/{format}"
        }
    }


@app.get("/api/stats", response_model=Stats)
async def get_stats():
    """Get database statistics"""
    conn = get_db()

    stats = {
        "total_entries": conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0],
        "entries_by_year": dict(conn.execute('''
            SELECT hebrew_year, COUNT(*) FROM entries
            WHERE hebrew_year IS NOT NULL
            GROUP BY hebrew_year ORDER BY hebrew_year
        ''').fetchall()),
        "entries_by_category": dict(conn.execute('''
            SELECT category, COUNT(*) FROM entries
            WHERE category IS NOT NULL
            GROUP BY category
        ''').fetchall()),
        "total_sources": conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
        "sources_by_type": dict(conn.execute('''
            SELECT source_type, COUNT(*) FROM sources
            WHERE source_type IS NOT NULL
            GROUP BY source_type
        ''').fetchall())
    }

    conn.close()
    return stats


@app.get("/api/entries", response_model=List[Entry])
async def get_entries(
    year: Optional[int] = Query(None, description="Hebrew year"),
    category: Optional[str] = Query(None, description="Content category"),
    parsha: Optional[str] = Query(None, description="Torah portion"),
    month: Optional[str] = Query(None, description="Hebrew month"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get entries with optional filters"""
    conn = get_db()

    query = "SELECT * FROM entries WHERE 1=1"
    params = []

    if year:
        query += " AND hebrew_year = ?"
        params.append(year)

    if category:
        query += " AND category = ?"
        params.append(category)

    if parsha:
        query += " AND parsha = ?"
        params.append(parsha)

    if month:
        query += " AND (hebrew_month = ? OR hebrew_month_translit = ?)"
        params.extend([month, month])

    query += " ORDER BY hebrew_year, hebrew_month, sequence LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [dict(row) for row in rows]


@app.get("/api/entries/{entry_id}", response_model=Entry)
async def get_entry(entry_id: int):
    """Get a specific entry by ID"""
    conn = get_db()

    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")

    return dict(row)


@app.get("/api/search")
async def search_entries(
    q: str = Query(..., description="Search query (Hebrew or English)"),
    limit: int = Query(50, ge=1, le=500)
):
    """Full-text search across entries"""
    conn = get_db()

    # Use FTS5 for full-text search
    query = '''
        SELECT e.* FROM entries e
        JOIN entries_fts fts ON e.id = fts.rowid
        WHERE entries_fts MATCH ?
        LIMIT ?
    '''

    rows = conn.execute(query, (q, limit)).fetchall()
    conn.close()

    return {
        "query": q,
        "count": len(rows),
        "results": [dict(row) for row in rows]
    }


@app.get("/api/years")
async def get_years():
    """Get all available Hebrew years with entry counts"""
    conn = get_db()

    years = conn.execute('''
        SELECT hebrew_year, COUNT(*) as count
        FROM entries
        WHERE hebrew_year IS NOT NULL
        GROUP BY hebrew_year
        ORDER BY hebrew_year
    ''').fetchall()

    conn.close()

    return [{"year": row["hebrew_year"], "count": row["count"]} for row in years]


@app.get("/api/parshas")
async def get_parshas():
    """Get all Torah portions with entry counts"""
    conn = get_db()

    parshas = conn.execute('''
        SELECT parsha, COUNT(*) as count
        FROM entries
        WHERE parsha IS NOT NULL
        GROUP BY parsha
        ORDER BY COUNT(*) DESC
    ''').fetchall()

    conn.close()

    return [{"parsha": row["parsha"], "count": row["count"]} for row in parshas]


@app.get("/api/categories")
async def get_categories():
    """Get all content categories with entry counts"""
    conn = get_db()

    categories = conn.execute('''
        SELECT category, COUNT(*) as count
        FROM entries
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY COUNT(*) DESC
    ''').fetchall()

    conn.close()

    return [{"category": row["category"], "count": row["count"]} for row in categories]


@app.get("/api/export/{format}")
async def export_data(format: str):
    """Export database in specified format"""
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")

    from db_setup import MafteiachDatabase
    db = MafteiachDatabase(DB_PATH)

    if format == "json":
        path = db.export_json('mafteiach_export.json')
    else:
        path = db.export_csv('mafteiach_export.csv')

    if path and Path(path).exists():
        return FileResponse(path, filename=Path(path).name)
    else:
        raise HTTPException(status_code=404, detail="Export file not found")


@app.get("/api/sources/{entry_id}")
async def get_entry_sources(entry_id: int):
    """Get all sources (PDFs, audio, video) for an entry"""
    conn = get_db()

    sources = conn.execute('''
        SELECT * FROM sources
        WHERE entry_id = ?
        ORDER BY source_type
    ''', (entry_id,)).fetchall()

    conn.close()

    return [dict(row) for row in sources]


if __name__ == "__main__":
    # Check if database exists
    if not Path(DB_PATH).exists():
        print(f"Database not found at {DB_PATH}")
        print("Run 'python db_setup.py' first to create the database")
        exit(1)

    print("Starting Mafteiach.app API server...")
    print("API documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
