import sqlite3

class DatabaseManager:
    def __init__(self, db_path="system_db/queu.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_connection(self):
        return self.conn

    def get_cursor(self):
        return self.cursor

    def close(self):
        self.conn.close() 
