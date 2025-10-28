# models.py
# Simple SQLite helpers for users and tasks

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

DB = os.path.join(os.path.dirname(__file__), "db.sqlite3")

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # users table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    # tasks table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        priority TEXT,
        status TEXT DEFAULT 'incomplete',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    conn.commit()
    conn.close()

def create_user(email, password):
    conn = get_conn()
    cur = conn.cursor()
    hashed = generate_password_hash(password)
    cur.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed))
    conn.commit()
    conn.close()

def find_user_by_email(email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    return row

def verify_user(email, password):
    row = find_user_by_email(email)
    if not row:
        return False
    return check_password_hash(row["password"], password)

def get_user_by_email(email):
    return find_user_by_email(email)

def create_task(user_id, title, description, due_date, priority):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (user_id, title, description, due_date, priority) VALUES (?, ?, ?, ?, ?)',
                (user_id, title, description, due_date, priority))
    conn.commit()
    conn.close()

def get_tasks_for_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_task(task_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_task(task_id, title, description, due_date, priority, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        UPDATE tasks
        SET title = ?, description = ?, due_date = ?, priority = ?, status = ?
        WHERE id = ?
    ''', (title, description, due_date, priority, status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

# Initialize database automatically if not exists
if not os.path.exists(DB):
    init_db()
