#!/usr/bin/env python3
import os, sys, time, sqlite3, argparse, datetime as dt, requests

DB_PATH = os.getenv("DB_PATH", "state.db")

# -------------------- Storage --------------------
def ensure_db(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS alerts (
            key TEXT PRIMARY KEY,
            last_price REAL,
            last_notified_price REAL,
            last_seen_at TEXT,
            last_notified_at TEXT
        )"""
    )
    conn.commit()

def load_alert(conn, key):
    cur = conn.execute("SELECT key,last_price,last_notified_price,last_seen_at,last_notified_at FROM alerts WHERE key=?",(key,))
    return cur.fetchone()

def save_alert(conn, key, last_price, last_notified_price, notified):
    now = dt.datetime.utcnow().isoformat()
    row = load_alert(conn,key)
    if row is None:
        conn.execute(
            "INSERT INTO alerts (key,last_price,last_notified_price,last_seen_at,last_notified_at) VALUES (?,?,?,?,?)",
            (key,last_price,last_notified_price if notified else None,now,now if notified else None)
        )
    else:
        conn.execute(
            "UPDATE alerts SET last_price=?,last_seen_at=?,last_notified_price=COALESCE(?,last_notified_price),last_notified_at=COALESCE(?,last_notified_at) WHERE key=?",
            (last_price,now,last_notified_price if notified else None,now if notified else None,key)
        )
    conn.commit()

# -------------------- Telegram --------------------
def notify_telegram(token,chat_id,text):
    url=f"https://api.telegram.org/bot{token}/sendMessage"
    r=requests.post(url,json={"chat_id":chat_id,"text":text,"parse_mode":"HTML","disable_web_page_preview":True},timeout=20)
    r.raise_for_status()

# -------------------- Amadeus --------------------
def amadeus_get_token(api_key,api_secret):
    r=requests.post("https://test.api.amadeus.com/v1/security/oauth2/token",
        data={"grant_type":"client_credentials","client_id":api_key,"client_secret":api_secret},timeout=20)
    r.raise_for_status()
    return r.json()["access_token"]

def amadeus_search(token,origin,destination,date_from,date_to,curr="ARS",adults=1,trip_type="round",nights_in_dst_from=None,nights_in_dst_to=None,non_stop_only=True):
    headers={"Authorization":f"Bearer {token}"}
    url="https://test.api.amadeus.com/v2/shopping/flight-offers"
    best=None; best_price=1e15
    start=dt.date.fromisoformat(date_from); end=dt.date.fromisoformat(date_to)
    d=start
    while d<=end:
        if trip_type=="oneway":
           params = {
    "originLocationCode": origin,
    "destinationLocationCode": destination,
    "departureDate": departure_date,
    "adults": 1,
    "currencyCode": "USD",
    "max": 5
}


