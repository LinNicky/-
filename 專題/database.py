import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

conn.execute('''create table if not exists users(
    username TEXT PRIMARY KEY,
    password TEXT,
    email TEXT
)''')