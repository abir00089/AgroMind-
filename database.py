import sqlite3
import pandas as pd
from datetime import datetime

def init_db():
    conn = sqlite3.connect('agromind.db', check_same_thread=False)
    c = conn.cursor()
    # Table for Plant Scans - Now includes the 'status' column for soil health
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (date TEXT, tree_id TEXT, health_score INTEGER, moisture INTEGER, status TEXT)''')
    # Table for Dynamic User Registration
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def create_account(u, p):
    try:
        conn = sqlite3.connect('agromind.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
        conn.commit()
        conn.close()
        return True
    except: return False

def login_user(u, p):
    conn = sqlite3.connect('agromind.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (u, p))
    res = c.fetchone()
    conn.close()
    return res

def save_scan(tree_id, score, moisture_val, status):
    conn = sqlite3.connect('agromind.db', check_same_thread=False)
    c = conn.cursor()
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO scans (date, tree_id, health_score, moisture, status) VALUES (?, ?, ?, ?, ?)", 
              (date_now, tree_id, score, moisture_val, status))
    conn.commit()
    conn.close()

def get_history(tree_id=None):
    conn = sqlite3.connect('agromind.db', check_same_thread=False)
    if tree_id and tree_id != "All Trees":
        query = f"SELECT * FROM scans WHERE tree_id = '{tree_id}' ORDER BY date DESC"
    else:
        query = "SELECT * FROM scans ORDER BY date DESC LIMIT 50"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_unique_trees():
    conn = sqlite3.connect('agromind.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT DISTINCT tree_id FROM scans")
    trees = [row[0] for row in c.fetchall()]
    conn.close()
    return trees

def clear_all_data():
    conn = sqlite3.connect('agromind.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM scans")
    conn.commit()
    conn.close()