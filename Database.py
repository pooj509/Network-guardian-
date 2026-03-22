import sqlite3

def get_db():
    conn = sqlite3.connect('network.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Create devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ip TEXT UNIQUE,
            mac TEXT UNIQUE,
            type TEXT,
            status TEXT,
            threat_level TEXT,
            cpu_usage INTEGER,
            memory_usage INTEGER,
            last_seen TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            device_name TEXT,
            message TEXT,
            severity TEXT,
            type TEXT,
            timestamp TEXT,
            is_resolved INTEGER DEFAULT 0,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database tables created!")

if __name__ == "__main__":
    init_db()
