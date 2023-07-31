import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS registration_table
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              chat_id INTEGER NOT NULL,
              name TEXT,
              age INTEGER,
              country TEXT,
              language TEXT,
              photo BLOB,
              username TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS likes_table
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_1 INTEGER NOT NULL,
              user_2 INTEGER NOT NULL,
              like INTEGER CHECK(like IN (0, 1)))''')

conn.commit()

