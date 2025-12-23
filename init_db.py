import sqlite3

def init_database():
    """Initialize the database with schema"""
    conn = sqlite3.connect('chirpx.db')
    
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()
