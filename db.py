import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/app.db")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = connect()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS families(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id INTEGER NOT NULL,
        display_name TEXT NOT NULL,
        role TEXT NOT NULL, -- admin, founder, nextgen
        access_code TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(family_id) REFERENCES families(id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS answers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        week INTEGER NOT NULL,
        question_index INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        answer_text TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(family_id) REFERENCES families(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    con.commit()
    con.close()

def now_iso():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def create_family(name:str, family_code:str):
    con = connect(); cur = con.cursor()
    cur.execute("INSERT INTO families(family_code,name,created_at) VALUES(?,?,?)", (family_code, name, now_iso()))
    con.commit()
    con.close()

def get_family_by_code(family_code:str):
    con = connect(); cur = con.cursor()
    row = cur.execute("SELECT * FROM families WHERE family_code=?", (family_code,)).fetchone()
    con.close()
    return row

def list_families():
    con = connect(); cur = con.cursor()
    rows = cur.execute("SELECT * FROM families ORDER BY created_at DESC").fetchall()
    con.close()
    return rows

def create_user(family_id:int, display_name:str, role:str, access_code:str):
    con = connect(); cur = con.cursor()
    cur.execute("INSERT INTO users(family_id,display_name,role,access_code,created_at) VALUES(?,?,?,?,?)",
                (family_id, display_name, role, access_code, now_iso()))
    con.commit(); con.close()

def list_users(family_id:int):
    con = connect(); cur = con.cursor()
    rows = cur.execute("SELECT * FROM users WHERE family_id=? ORDER BY created_at ASC", (family_id,)).fetchall()
    con.close()
    return rows

def auth_user(family_id:int, access_code:str):
    con = connect(); cur = con.cursor()
    row = cur.execute("SELECT * FROM users WHERE family_id=? AND access_code=?", (family_id, access_code)).fetchone()
    con.close()
    return row

def upsert_answer(family_id:int, user_id:int, week:int, question_index:int, question_text:str, answer_text:str):
    con = connect(); cur = con.cursor()
    existing = cur.execute("""SELECT id FROM answers
                              WHERE family_id=? AND user_id=? AND week=? AND question_index=?""",
                           (family_id, user_id, week, question_index)).fetchone()
    if existing:
        cur.execute("UPDATE answers SET answer_text=?, updated_at=? WHERE id=?",
                    (answer_text, now_iso(), existing["id"]))
    else:
        cur.execute("""INSERT INTO answers(family_id,user_id,week,question_index,question_text,answer_text,updated_at)
                       VALUES(?,?,?,?,?,?,?)""",
                    (family_id, user_id, week, question_index, question_text, answer_text, now_iso()))
    con.commit(); con.close()

def get_answers_for_user(family_id:int, user_id:int, week:int):
    con = connect(); cur = con.cursor()
    rows = cur.execute("""SELECT * FROM answers WHERE family_id=? AND user_id=? AND week=?
                          ORDER BY question_index ASC""",
                       (family_id, user_id, week)).fetchall()
    con.close(); return rows

def get_all_answers(family_id:int):
    con = connect(); cur = con.cursor()
    rows = cur.execute("""SELECT a.*, u.display_name, u.role
                          FROM answers a JOIN users u ON a.user_id=u.id
                          WHERE a.family_id=?
                          ORDER BY a.week ASC, u.role ASC, u.display_name ASC, a.question_index ASC""",
                       (family_id,)).fetchall()
    con.close(); return rows
