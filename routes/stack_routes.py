"""
Stack routes — Tool & app stack management.
Pre-populated with common tools (Google Workspace, APIs, web apps).
Users can add custom tools with icons, notes, and credentials.
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════════

class StackTool(BaseModel):
    name: str
    category: str  # "ai-api", "google-workspace", "web-app", "dev-tool", "other"
    url: Optional[str] = None
    icon: Optional[str] = None  # emoji or icon name
    notes: Optional[str] = None
    credentials: Optional[str] = None  # encrypted or masked
    api_key_masked: Optional[str] = None
    usage_limit: Optional[str] = None
    cost_per_unit: Optional[str] = None
    tags: list[str] = []

class StackToolUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    notes: Optional[str] = None
    credentials: Optional[str] = None
    api_key_masked: Optional[str] = None
    usage_limit: Optional[str] = None
    cost_per_unit: Optional[str] = None
    tags: Optional[list[str]] = None


# ═══════════════════════════════════════════════════════════════
# Pre-populated tools
# ═══════════════════════════════════════════════════════════════

DEFAULT_TOOLS = [
    # Google Workspace
    {"name": "Gmail", "category": "google-workspace", "url": "https://mail.google.com", "icon": "📧", "tags": ["email", "google"]},
    {"name": "Google Drive", "category": "google-workspace", "url": "https://drive.google.com", "icon": "📁", "tags": ["storage", "google"]},
    {"name": "Google Docs", "category": "google-workspace", "url": "https://docs.google.com", "icon": "📝", "tags": ["docs", "google"]},
    {"name": "Google Sheets", "category": "google-workspace", "url": "https://sheets.google.com", "icon": "📊", "tags": ["spreadsheet", "google"]},
    {"name": "Google Calendar", "category": "google-workspace", "url": "https://calendar.google.com", "icon": "📅", "tags": ["calendar", "google"]},
    {"name": "Google Meet", "category": "google-workspace", "url": "https://meet.google.com", "icon": "📹", "tags": ["video", "google"]},

    # AI APIs
    {"name": "OpenAI", "category": "ai-api", "url": "https://platform.openai.com", "icon": "🧠", "tags": ["ai", "api", "llm"]},
    {"name": "Anthropic Claude", "category": "ai-api", "url": "https://console.anthropic.com", "icon": "🤖", "tags": ["ai", "api", "llm"]},
    {"name": "DeepSeek", "category": "ai-api", "url": "https://platform.deepseek.com", "icon": "🔍", "tags": ["ai", "api", "llm"]},
    {"name": "MiniMax", "category": "ai-api", "url": "https://api.minimax.io", "icon": "⚡", "tags": ["ai", "api", "llm"]},
    {"name": "Google Gemini", "category": "ai-api", "url": "https://aistudio.google.com", "icon": "💎", "tags": ["ai", "api", "llm"]},
    {"name": "Groq", "category": "ai-api", "url": "https://console.groq.com", "icon": "⚡", "tags": ["ai", "api", "llm"]},
    {"name": "OpenRouter", "category": "ai-api", "url": "https://openrouter.ai", "icon": "🔀", "tags": ["ai", "api", "router"]},

    # Web Apps
    {"name": "GitHub", "category": "web-app", "url": "https://github.com", "icon": "🐙", "tags": ["code", "git"]},
    {"name": "Supabase", "category": "web-app", "url": "https://supabase.com", "icon": "🟢", "tags": ["database", "backend"]},
    {"name": "Vercel", "category": "web-app", "url": "https://vercel.com", "icon": "▲", "tags": ["deploy", "hosting"]},
    {"name": "Notion", "category": "web-app", "url": "https://notion.so", "icon": "📋", "tags": ["docs", "wiki"]},
    {"name": "Obsidian", "category": "web-app", "url": "https://obsidian.md", "icon": "💎", "tags": ["notes", "knowledge"]},
    {"name": "Linear", "category": "web-app", "url": "https://linear.app", "icon": "📐", "tags": ["project", "tasks"]},

    # Dev Tools
    {"name": "Docker", "category": "dev-tool", "icon": "🐳", "tags": ["container", "dev"]},
    {"name": "VS Code", "category": "dev-tool", "icon": "💻", "tags": ["editor", "ide"]},
    {"name": "Postman", "category": "dev-tool", "url": "https://postman.com", "icon": "📮", "tags": ["api", "testing"]},
    {"name": "Termius", "category": "dev-tool", "icon": "🔌", "tags": ["ssh", "terminal"]},
]


# ═══════════════════════════════════════════════════════════════
# In-memory store (SQLite-backed in production)
# ═══════════════════════════════════════════════════════════════

# Use RAVEN's SQLite DB
def _get_db():
    from core.database import SessionLocal
    return SessionLocal()


def _ensure_table():
    """Create stack_tools table if it doesn't exist."""
    db = _get_db()
    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS stack_tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'other',
                url TEXT,
                icon TEXT,
                notes TEXT,
                credentials TEXT,
                api_key_masked TEXT,
                usage_limit TEXT,
                cost_per_unit TEXT,
                tags TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Seed defaults if table is empty
        count = db.execute("SELECT COUNT(*) FROM stack_tools").fetchone()[0]
        if count == 0:
            for tool in DEFAULT_TOOLS:
                db.execute("""
                    INSERT INTO stack_tools (name, category, url, icon, tags)
                    VALUES (?, ?, ?, ?, ?)
                """, (tool["name"], tool["category"], tool.get("url"), tool.get("icon"), json.dumps(tool.get("tags", []))))
        db.commit()
    except Exception as e:
        logger.error(f"Stack table init error: {e}")
        db.rollback()
    finally:
        db.close()


_ensure_table()


# ═══════════════════════════════════════════════════════════════
# Routes
# ═══════════════════════════════════════════════════════════════

def setup_stack_routes() -> APIRouter:
    router = APIRouter(prefix="/api/stack", tags=["stack"])

    @router.get("/tools")
    async def list_tools(category: Optional[str] = None, search: Optional[str] = None):
        """List all tools in the stack, optionally filtered."""
        db = _get_db()
        try:
            query = "SELECT * FROM stack_tools WHERE 1=1"
            params = []
            if category:
                query += " AND category = ?"
                params.append(category)
            if search:
                query += " AND (name LIKE ? OR notes LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%"])
            query += " ORDER BY category, name"
            rows = db.execute(query, params).fetchall()
            tools = []
            for row in rows:
                tools.append({
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "url": row[3],
                    "icon": row[4],
                    "notes": row[5],
                    "credentials": row[6],
                    "api_key_masked": row[7],
                    "usage_limit": row[8],
                    "cost_per_unit": row[9],
                    "tags": json.loads(row[10]) if row[10] else [],
                    "created_at": str(row[11]) if row[11] else None,
                    "updated_at": str(row[12]) if row[12] else None,
                })
            return {"tools": tools, "count": len(tools)}
        finally:
            db.close()

    @router.post("/tools")
    async def add_tool(tool: StackTool, request: Request):
        """Add a new tool to the stack."""
        db = _get_db()
        try:
            cursor = db.execute("""
                INSERT INTO stack_tools (name, category, url, icon, notes, credentials, api_key_masked, usage_limit, cost_per_unit, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tool.name, tool.category, tool.url, tool.icon, tool.notes,
                tool.credentials, tool.api_key_masked, tool.usage_limit,
                tool.cost_per_unit, json.dumps(tool.tags)
            ))
            db.commit()
            return {"id": cursor.lastrowid, "name": tool.name, "status": "created"}
        except Exception as e:
            db.rollback()
            raise HTTPException(500, str(e))
        finally:
            db.close()

    @router.put("/tools/{tool_id}")
    async def update_tool(tool_id: int, updates: StackToolUpdate):
        """Update an existing tool."""
        db = _get_db()
        try:
            existing = db.execute("SELECT * FROM stack_tools WHERE id = ?", (tool_id,)).fetchone()
            if not existing:
                raise HTTPException(404, "Tool not found")

            fields = {}
            for key in ["name", "category", "url", "icon", "notes", "credentials", "api_key_masked", "usage_limit", "cost_per_unit"]:
                val = getattr(updates, key, None)
                if val is not None:
                    fields[key] = val
            if updates.tags is not None:
                fields["tags"] = json.dumps(updates.tags)

            if fields:
                fields["updated_at"] = "CURRENT_TIMESTAMP"
                set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
                db.execute(f"UPDATE stack_tools SET {set_clause} WHERE id = ?", list(fields.values()) + [tool_id])
                db.commit()
            return {"id": tool_id, "status": "updated"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(500, str(e))
        finally:
            db.close()

    @router.delete("/tools/{tool_id}")
    async def delete_tool(tool_id: int):
        """Remove a tool from the stack."""
        db = _get_db()
        try:
            db.execute("DELETE FROM stack_tools WHERE id = ?", (tool_id,))
            db.commit()
            return {"id": tool_id, "status": "deleted"}
        except Exception as e:
            db.rollback()
            raise HTTPException(500, str(e))
        finally:
            db.close()

    @router.get("/categories")
    async def list_categories():
        """List all tool categories with counts."""
        db = _get_db()
        try:
            rows = db.execute("SELECT category, COUNT(*) as cnt FROM stack_tools GROUP BY category ORDER BY cnt DESC").fetchall()
            return [{"category": r[0], "count": r[1]} for r in rows]
        finally:
            db.close()

    return router
