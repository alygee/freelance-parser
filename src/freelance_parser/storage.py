import sqlite3

from .models import Order


class Storage:
    """Запоминает уже отправленные заказы, чтобы не слать дубли."""

    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS seen ("
            " source TEXT, id TEXT, title TEXT, url TEXT,"
            " created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            " PRIMARY KEY (source, id))"
        )

    def add_if_new(self, order: Order) -> bool:
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO seen (source, id, title, url) VALUES (?, ?, ?, ?)",
            (order.source, order.id, order.title, order.url),
        )
        self.conn.commit()
        return cur.rowcount == 1
