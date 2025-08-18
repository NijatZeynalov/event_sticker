import sqlite3

def init_db():
    conn = sqlite3.connect('stickers.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT 0
        )
    ''')

    # Create stickers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stickers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            image_file TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sticker_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (sticker_id) REFERENCES stickers (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
