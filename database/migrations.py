from db_contoller import DBContoller

# СТРУКТУРА ТАБЛИЦ
TABLES = ('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL UNIQUE,
        uk_url TEXT,
        us_url TEXT,
        created_at TIMESTAMP NOT NULL
    )
    ''', '''
    CREATE TABLE IF NOT EXISTS word_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER UNIQUE NOT NULL,
        checks_count INTEGER NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (word_id) REFERENCES words (id)
    )
    ''', '''
    CREATE TABLE IF NOT EXISTS meaning_blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (word_id) REFERENCES words (id)
    )
    ''', '''
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER,
        block_id INTEGER NOT NULL,
        translation TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (block_id) REFERENCES meaning_blocks (id),
        FOREIGN KEY (word_id) REFERENCES words (id)
    )
    ''', '''
    CREATE TABLE IF NOT EXISTS definitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER,
        block_id INTEGER NOT NULL,
        definition TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (block_id) REFERENCES meaning_blocks (id),
        FOREIGN KEY (word_id) REFERENCES words (id)
    )
    ''', '''
    CREATE TABLE IF NOT EXISTS examples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER,
        block_id INTEGER NOT NULL,
        example TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (block_id) REFERENCES meaning_blocks (id),
        FOREIGN KEY (word_id) REFERENCES words (id)
    )
    ''')


def migrate():
    db = DBContoller('database/glossary.db')
    cursor = db.conn.cursor()
    # Create tables
    for table in TABLES:
        cursor.execute(table)
    db.conn.commit()
    db.close()


migrate()
