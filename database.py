import os
import sqlite3
from datetime import datetime
from pathlib import Path

# 数据保存位置：%LOCALAPPDATA%\ClipNest\history.db
# 放在用户目录而不是项目目录，避免被误提交到 GitHub
DB_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ClipNest"
DB_PATH = DB_DIR / "history.db"

# 最多保留多少条未置顶记录
MAX_ITEMS = 500


class Database:
    def __init__(self, path=DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self):
        """建表。IF NOT EXISTS 保证重复启动不会报错，也方便以后加字段。"""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clips (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                content    TEXT NOT NULL UNIQUE,
                pinned     INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add(self, content):
        """保存一条记录。内容已存在时只更新时间，不重复插入。"""
        now = datetime.now().isoformat(timespec="seconds")
        row = self.conn.execute(
            "SELECT id FROM clips WHERE content = ?", (content,)
        ).fetchone()

        if row is not None:
            self.conn.execute(
                "UPDATE clips SET updated_at = ? WHERE id = ?", (now, row["id"])
            )
        else:
            self.conn.execute(
                "INSERT INTO clips (content, pinned, created_at, updated_at) "
                "VALUES (?, 0, ?, ?)",
                (content, now, now),
            )
            self.trim()

        self.conn.commit()

    def trim(self):
        """只保留最新的 MAX_ITEMS 条未置顶记录，防止数据库无限增长。"""
        self.conn.execute(
            """
            DELETE FROM clips
            WHERE pinned = 0 AND id NOT IN (
                SELECT id FROM clips
                WHERE pinned = 0
                ORDER BY updated_at DESC, id DESC
                LIMIT ?
            )
            """,
            (MAX_ITEMS,),
        )

    def list_clips(self, keyword=""):
        """置顶的排最前，其余按最近使用时间排序；keyword 不为空时做模糊搜索。"""
        if keyword:
            return self.conn.execute(
                "SELECT * FROM clips WHERE content LIKE ? "
                "ORDER BY pinned DESC, updated_at DESC, id DESC",
                (f"%{keyword}%",),
            ).fetchall()
        return self.conn.execute(
            "SELECT * FROM clips ORDER BY pinned DESC, updated_at DESC, id DESC"
        ).fetchall()

    def set_pinned(self, clip_id, pinned):
        self.conn.execute(
            "UPDATE clips SET pinned = ? WHERE id = ?",
            (1 if pinned else 0, clip_id),
        )
        self.conn.commit()

    def delete(self, clip_id):
        self.conn.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
        self.conn.commit()

    def clear_unpinned(self):
        """清空所有未置顶记录，置顶内容不受影响。"""
        self.conn.execute("DELETE FROM clips WHERE pinned = 0")
        self.conn.commit()

    def close(self):
        self.conn.close()
