import sqlite3
import datetime

DB_NAME = 'tetrizos_scores.db'

def inicializar_banco_dados():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nickname TEXT NOT NULL,
        pontuacao INTEGER NOT NULL,
        duracao_segundos INTEGER NOT NULL,
        data_hora TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def salvar_score_db(nickname, pontuacao, duracao_segundos):
    if not nickname.strip():
        nickname = "ANONIMO"
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    data_hora_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO scores (nickname, pontuacao, duracao_segundos, data_hora) VALUES (?, ?, ?, ?)",
              (nickname, pontuacao, duracao_segundos, data_hora_str))
    
    last_id = c.lastrowid
    
    conn.commit()
    conn.close()
    
    return last_id

def carregar_ultimos_scores_db(limit=5):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, nickname, pontuacao, duracao_segundos FROM scores ORDER BY pontuacao DESC LIMIT ?", (limit,))
    scores = c.fetchall()
    conn.close()
    return scores