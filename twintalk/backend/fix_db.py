import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "digital_twin.db")
print(f"Fixing db at {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("UPDATE direct_messages SET sender_mode='user' WHERE sender_mode='agent';")
changes = conn.total_changes
conn.commit()
conn.close()

print(f"Fixed {changes} rows.")
