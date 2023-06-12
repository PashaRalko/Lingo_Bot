import sqlite3
from PIL import Image

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS images
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              chat_id INTEGER NOT NULL,
              name TEXT NOT NULL,
              age INTEGER NOT NULL,
              country TEXT NOT NULL,
              language TEXT NOT NULL,
              photo BLOB NOT NULL)''')

conn.commit()

