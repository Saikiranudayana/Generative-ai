import sqlite3
import os
from pathlib import Path

# Create a simple students database if it doesn't exist
db_path = Path('students.db')
if not db_path.exists():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
    CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        grade TEXT,
        email TEXT
    )
    ''')
    
    # Insert sample data
    students_data = [
        (1, 'Alice Johnson', 20, 'A', 'alice@example.com'),
        (2, 'Bob Smith', 22, 'B', 'bob@example.com'),
        (3, 'Charlie Brown', 21, 'A', 'charlie@example.com'),
        (4, 'Diana Prince', 23, 'A', 'diana@example.com'),
        (5, 'Eve Wilson', 19, 'B', 'eve@example.com')
    ]
    
    cursor.executemany('INSERT INTO students VALUES (?, ?, ?, ?, ?)', students_data)
    conn.commit()
    conn.close()
    print('Database created successfully with sample data!')
else:
    print('Database already exists')
