# init_db.py
import sqlite3

def init_db():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            fee REAL,
            virtual_account TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
