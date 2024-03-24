import sqlite3
import json

db_file = "path_to_your_database.db"


def create_connection():
    """Создает соединение с базой данных SQLite."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
        return None


def create_table():
    """Создает таблицу пользователей, если она не существует."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            settings TEXT
        );
        """)
        conn.commit()
        conn.close()


def update_user_settings(user_id, theme=None, level=None):
    """Обновляет настройки пользователя."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT settings FROM users WHERE id = ?", (user_id,))
        settings = cursor.fetchone()
        if settings:
            settings = json.loads(settings[0])
        else:
            settings = {}
        if theme: settings['theme'] = theme
        if level: settings['level'] = level

        # Проверяем, существует ли пользователь, и обновляем его настройки или добавляем нового
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users (id, settings) VALUES (?, ?)", (user_id, json.dumps(settings)))
        else:
            cursor.execute("UPDATE users SET settings = ? WHERE id = ?", (json.dumps(settings), user_id))

        conn.commit()
        conn.close()


def get_user_settings(user_id):
    """Возвращает настройки пользователя."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT settings FROM users WHERE id = ?", (user_id,))
        settings = cursor.fetchone()
        conn.close()
        return json.loads(settings[0]) if settings else {}


def add_settings_column():
    """Добавляет столбец settings в таблицу users, если он отсутствует."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("""
        ALTER TABLE users ADD COLUMN settings TEXT
        """)
        conn.commit()
        conn.close()


def recreate_table():
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        create_table()
        conn.close()


# После добавления этих функций, убедитесь, что таблица создается при старте вашего приложения
create_table()

# Теперь вы можете использовать эти функции для работы с настройками пользователей
