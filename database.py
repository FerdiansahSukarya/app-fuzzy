import mysql.connector
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",  # ganti sesuai setting
        database="sensor_db"
    )

def simpan_sensor_mysql(ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """INSERT INTO sensor (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status)
             VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(sql, (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status))
    conn.commit()
    cursor.close()
    conn.close()

def simpan_relay_mysql(ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, aksi, relay_status):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """INSERT INTO relay (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, aksi, relay_status)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, aksi, relay_status))
    conn.commit()
    cursor.close()
    conn.close()

def simpan_fuzzy_log(ph, ph_status, kelembaban, kelembaban_status, durasi):
    db = get_connection()
    cursor = db.cursor()
    query = """
        INSERT INTO fuzzy_log (waktu, ph, ph_status, kelembaban, kelembaban_status, durasi)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    now = datetime.now()
    cursor.execute(query, (now, ph, ph_status, kelembaban, kelembaban_status, durasi))
    db.commit()
    cursor.close()
    db.close()
