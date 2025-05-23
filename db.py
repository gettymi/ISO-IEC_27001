import psycopg2
import streamlit as st

def init_connection():
    return psycopg2.connect(
        host=st.secrets["db_host"],
        database=st.secrets["db_name"],
        user=st.secrets["db_user"],
        password=st.secrets["db_password"]
    )

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS risks (
                id SERIAL PRIMARY KEY,
                name TEXT,
                probability INTEGER,
                impact INTEGER,
                confidentiality BOOLEAN,
                availability BOOLEAN
            )
        """)
        conn.commit()

def insert_risk(conn, name, prob, impact, conf, avail):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO risks (name, probability, impact, confidentiality, availability)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, prob, impact, conf, avail))
        conn.commit()

def fetch_risks(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, probability, impact, confidentiality, availability FROM risks")
        return cur.fetchall()
