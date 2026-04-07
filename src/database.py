import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/alerts.db")

# Database helper functions for managing alert records.
def get_connection():
    """Create and return a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

# Database initialization and alert management functions.
def init_db():
    """Create the alerts table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            alert_type  TEXT    NOT NULL,
            message     TEXT    NOT NULL,
            daily_spend REAL,
            threshold   REAL,
            projected   REAL
        )
    """)
    conn.commit()
    conn.close()

# Alert logging and retrieval functions.
def log_alert(alert_type, message, daily_spend=None, threshold=None, projected=None):
    """Insert a new alert record into the database."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (timestamp, alert_type, message, daily_spend, threshold, projected)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        alert_type,
        message,
        daily_spend,
        threshold,
        projected
    ))
    
    # Commit the transaction and close the connection.
    conn.commit()
    conn.close()

# Fetching recent alerts for display in the dashboard.
def get_recent_alerts(limit=10):
    """Fetch the most recent alerts from the database."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, alert_type, message, daily_spend, threshold, projected
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    # Fetch all rows and close the connection.
    rows = cursor.fetchall()
    conn.close()

    return rows