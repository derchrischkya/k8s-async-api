import sqlite3

class SQLLITE:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS requests (id TEXT, message TEXT, completed BOOLEAN, requester TEXT, timestamp TEXT, queue TEXT)")
        self.conn.commit()
        
    def insert(self, id, message, completed, requester, timestamp, queue):
        self.cursor.execute("INSERT INTO requests (id, message, completed, requester, timestamp, queue) VALUES (?, ?, ?, ?, ?, ?)", (id, message, completed, requester, timestamp, queue))
        self.conn.commit()
    
    def update(self, id, message=None, completed=None, requester=None, timestamp=None, queue=None):
        # Only update fields that are not None
        fields = {}
        if message is not None:
            fields["message"] = message
        if completed is not None:
            fields["completed"] = completed
        if requester is not None:
            fields["requester"] = requester
        if timestamp is not None:
            fields["timestamp"] = timestamp
        if queue is not None:
            fields["queue"] = queue
        # Create the update string
        update_str = ", ".join([f"{key}='{value}'" for key, value in fields.items()])
        self.cursor.execute(f"UPDATE requests SET {update_str} WHERE id=?", (id,))
        self.conn.commit()
        
    def get_all(self):
        self.cursor.execute("SELECT message, completed, requester, timestamp, queue FROM requests")
        return self.cursor.fetchall()
    
    def get(self, id):
        self.cursor.execute("SELECT message, completed, requester, timestamp, queue FROM requests WHERE id=?", (id,))
        return self.cursor.fetchone()
        
    def close(self):
        self.conn.close()