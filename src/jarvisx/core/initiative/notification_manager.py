import logging
import uuid
from .initiative_store import InitiativeStore

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Queues proactive alerts to be read by the Voice Router during ambient listening.
    """
    def __init__(self, store: InitiativeStore):
        self.store = store

    def queue_notification(self, recommendation_id: str, message: str):
        self.store.conn.execute(
            "INSERT INTO notifications (id, recommendation_id, message) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), recommendation_id, message)
        )
        self.store.conn.commit()

    def get_unread_notifications(self) -> list:
        cursor = self.store.conn.execute("SELECT * FROM notifications WHERE is_read = FALSE")
        rows = cursor.fetchall()
        
        # Mark as read
        for row in rows:
            self.store.conn.execute("UPDATE notifications SET is_read = TRUE WHERE id = ?", (row["id"],))
        self.store.conn.commit()
        
        return [dict(row) for row in rows]
