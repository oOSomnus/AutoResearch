"""
History Module - SQLite-based analysis history management.
"""
import os
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class HistoryEntry:
    """A single history entry."""
    id: int
    source: str
    title: str
    paper_type: str
    analyzed_at: str
    output_format: str
    language: str
    report_path: Optional[str]
    checkpoint_path: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "paper_type": self.paper_type,
            "analyzed_at": self.analyzed_at,
            "output_format": self.output_format,
            "language": self.language,
            "report_path": self.report_path,
            "checkpoint_path": self.checkpoint_path
        }


class HistoryManager:
    """Manages analysis history using SQLite."""

    def __init__(self, db_path: str = ".history.db"):
        """
        Initialize the history manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    title TEXT,
                    paper_type TEXT DEFAULT 'unknown',
                    analyzed_at TEXT NOT NULL,
                    output_format TEXT DEFAULT 'markdown',
                    language TEXT DEFAULT 'zh',
                    report_path TEXT,
                    checkpoint_path TEXT,
                    background TEXT,
                    innovation TEXT,
                    results TEXT
                )
            """)
            conn.commit()

    def add_entry(self, state: Dict[str, Any]) -> int:
        """
        Add a new history entry.

        Args:
            state: The analysis state

        Returns:
            ID of the inserted entry
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_history (
                    source, title, paper_type, analyzed_at,
                    output_format, language, report_path, checkpoint_path,
                    background, innovation, results
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.get("source", ""),
                state.get("title", ""),
                state.get("paper_type", "unknown"),
                datetime.now().isoformat(),
                state.get("output_format", "markdown"),
                state.get("language", "zh"),
                state.get("report_path", ""),
                state.get("checkpoint_path", ""),
                state.get("background", ""),
                state.get("innovation", ""),
                state.get("results", "")
            ))
            conn.commit()
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[HistoryEntry]:
        """
        Get a history entry by ID.

        Args:
            entry_id: The entry ID

        Returns:
            HistoryEntry or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, source, title, paper_type, analyzed_at,
                       output_format, language, report_path, checkpoint_path
                FROM analysis_history
                WHERE id = ?
            """, (entry_id,))
            row = cursor.fetchone()
            if row:
                return HistoryEntry(
                    id=row["id"],
                    source=row["source"],
                    title=row["title"] or "",
                    paper_type=row["paper_type"],
                    analyzed_at=row["analyzed_at"],
                    output_format=row["output_format"],
                    language=row["language"],
                    report_path=row["report_path"],
                    checkpoint_path=row["checkpoint_path"]
                )
        return None

    def list_entries(self, limit: int = 20, offset: int = 0,
                    paper_type: Optional[str] = None,
                    language: Optional[str] = None) -> List[HistoryEntry]:
        """
        List history entries.

        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            paper_type: Filter by paper type
            language: Filter by language

        Returns:
            List of HistoryEntry objects
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
                SELECT id, source, title, paper_type, analyzed_at,
                       output_format, language, report_path, checkpoint_path
                FROM analysis_history
            """
            params = []

            if paper_type:
                query += " WHERE paper_type = ?"
                params.append(paper_type)
            elif language:
                query += " WHERE language = ?"
                params.append(language)

            query += " ORDER BY analyzed_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                HistoryEntry(
                    id=row["id"],
                    source=row["source"],
                    title=row["title"] or "",
                    paper_type=row["paper_type"],
                    analyzed_at=row["analyzed_at"],
                    output_format=row["output_format"],
                    language=row["language"],
                    report_path=row["report_path"],
                    checkpoint_path=row["checkpoint_path"]
                )
                for row in rows
            ]

    def search(self, query: str, limit: int = 20) -> List[HistoryEntry]:
        """
        Search history entries by title or source.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching HistoryEntry objects
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, source, title, paper_type, analyzed_at,
                       output_format, language, report_path, checkpoint_path
                FROM analysis_history
                WHERE title LIKE ? OR source LIKE ?
                ORDER BY analyzed_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            rows = cursor.fetchall()

            return [
                HistoryEntry(
                    id=row["id"],
                    source=row["source"],
                    title=row["title"] or "",
                    paper_type=row["paper_type"],
                    analyzed_at=row["analyzed_at"],
                    output_format=row["output_format"],
                    language=row["language"],
                    report_path=row["report_path"],
                    checkpoint_path=row["checkpoint_path"]
                )
                for row in rows
            ]

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a history entry.

        Args:
            entry_id: The entry ID

        Returns:
            True if deleted, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM analysis_history WHERE id = ?",
                (entry_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self) -> int:
        """
        Delete all history entries.

        Returns:
            Number of entries deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM analysis_history")
            conn.commit()
            return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the history.

        Returns:
            Dictionary with statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total count
            cursor.execute("SELECT COUNT(*) FROM analysis_history")
            total = cursor.fetchone()[0]

            # Count by paper type
            cursor.execute("""
                SELECT paper_type, COUNT(*) as count
                FROM analysis_history
                GROUP BY paper_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}

            # Count by language
            cursor.execute("""
                SELECT language, COUNT(*) as count
                FROM analysis_history
                GROUP BY language
            """)
            by_language = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                "total_entries": total,
                "by_paper_type": by_type,
                "by_language": by_language
            }


# Global history manager instance
_global_history_manager: Optional[HistoryManager] = None


def get_history_manager(db_path: str = ".history.db") -> HistoryManager:
    """
    Get or create the global history manager.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        The global history manager instance
    """
    global _global_history_manager

    if _global_history_manager is None:
        _global_history_manager = HistoryManager(db_path)

    return _global_history_manager