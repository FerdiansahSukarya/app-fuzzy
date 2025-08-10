from flask import Flask, render_template, jsonify, request
from fuzzy import evaluasi_fuzzy, siram_air
import threading
import time
from sensor_reader import baca_ph, baca_kelembaban
from relay_control import RelayControl
from supabase_client import simpan_fuzzy_log_supabase, simpan_sensor_supabase, simpan_relay_supabase
from db import get_connection
import requests
from datetime import datetime

app = Flask(__name__)
hasil_terakhir = {}
relay_ctrl = RelayControl()
manual_mode = False  # flag mode manual aktif atau tidak
manual_status = False  # status relay manual ON/OFF
status_relay_supabase_sebelumnya = False 

def fuzzy_loop():

    global hasil_terakhir, status_relay_supabase_sebelumnya

    status_relay_sebelumnya = False

    while True:
        ph_value, ph_label = baca_ph()
        kelembaban_adc, kelembaban_persen, kelembaban_label = baca_kelembaban()

        # Simpan data sensor ke DB MySQL
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sensor (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status)
                VALUES (%s, %s, %s, %s, %s)
            """, (ph_value, ph_label, kelembaban_adc, kelembaban_persen, kelembaban_label))
            conn.commit()
            cursor.close()
            conn.close()

            try:
                simpan_sensor_supabase(
                ph=ph_value,
                ph_status=ph_label,
                kelembaban_adc=kelembaban_adc,
                kelembaban_persen=kelembaban_persen,
                kelembaban_status=kelembaban_label
                )
            except Exception as e:
                print(f"[ERROR] Gagal simpan data sensor ke Supabase: {e}")
    
        except Exception as e:
            print(f"[ERROR] Gagal simpan data sensor: {e}")

        hasil = evaluasi_fuzzy(ph_value, kelembaban_adc)
        hasil["ph_label"] = ph_label
        hasil["kelembaban_persen"] = kelembaban_persen
        hasil["kelembaban_status"] = kelembaban_label

        hasil_terakhir = hasil

        status_relay_saat_ini = hasil["durasi"] > 0

        if status_relay_saat_ini and not status_relay_sebelumnya:
            # Jalankan relay
            siram_air(hasil["durasi"])
            print(f"[RELAY] Menyiram {hasil['durasi']} detik")

            # Simpan log relay ON
            try:
                cursor.execute("""
                    INSERT INTO relay (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, aksi, relay_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (ph_value, ph_label, kelembaban_adc, kelembaban_persen, kelembaban_label, hasil["durasi"], "SIRAM", 1))
                conn.commit()
            except Exception as e:
                print(f"[ERROR] Gagal simpan log relay ON: {e}")

        elif not status_relay_saat_ini and status_relay_sebelumnya:
            print("[RELAY] Tidak menyiram")
            conn = get_connection()
            cursor = conn.cursor()
            # Simpan log relay OFF
            try:
                cursor.execute("""
                    INSERT INTO relay (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, aksi, relay_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (ph_value, ph_label, kelembaban_adc, kelembaban_persen, kelembaban_label, 0, "TIDAK SIRAM", 0))
                conn.commit()

                cursor.close()
                conn.close()
            except Exception as e:
                print(f"[ERROR] Gagal simpan log relay OFF: {e}")

        if status_relay_saat_ini != status_relay_supabase_sebelumnya:
            try:
                simpan_fuzzy_log_supabase(
                    hasil["ph"],
                    hasil["ph_status"],
                    hasil["kelembaban"],
                    hasil["kelembaban_status"],
                    hasil["durasi"],
                    status_relay_saat_ini
                )
                print(f"[SUPABASE] Log disimpan (relay {'ON' if status_relay_saat_ini else 'OFF'})")
                status_relay_supabase_sebelumnya = status_relay_saat_ini
            except Exception as e:
                print(f"[ERROR] Gagal simpan log relay ke Supabase: {e}")

        status_relay_sebelumnya = status_relay_saat_ini

        cursor.close()
        conn.close()
    

        time.sleep(10)



@app.route("/riwayat")
def riwayat():
    return render_template("riwayat.html")

@app.route("/api/riwayat")
def api_riwayat():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
    SELECT waktu, ph, ph_status, kelembaban_adc AS kelembaban, kelembaban_status, durasi, aksi
    FROM relay
    ORDER BY waktu DESC
    LIMIT 30
""")

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    relay_status_fuzzy = hasil_terakhir.get("durasi", 0) > 0

    # Jika mode manual aktif, relay_status dari manual_status, else dari fuzzy
    if manual_mode:
        relay_status = manual_status
    else:
        relay_status = relay_status_fuzzy

    return jsonify({
        **hasil_terakhir,
        "relay": {
            "aktif": relay_status,
            "manual_mode": manual_mode
        }
    })


@app.route("/api/relay/manual", methods=["POST"])
def api_relay_manual():
    global manual_mode, manual_status

    data = request.json
    action = data.get("action")

    if action not in ["on", "off"]:
        return jsonify({"error": "Invalid action"}), 400

    manual_mode = True

    if action == "on":
        started = relay_ctrl.start_relay()
        manual_status = started or relay_ctrl.is_running()
        aksi = "SIRAM"
        durasi = data.get("durasi", 20)  # misal default durasi 20 detik
    else:
        stopped = relay_ctrl.stop_relay()
        manual_status = False
        aksi = "TIDAK SIRAM"
        durasi = 0

    # Ambil data sensor terbaru dari hasil_terakhir
    ph = hasil_terakhir.get("ph", 0)
    ph_status = hasil_terakhir.get("ph_status", "")
    kelembaban_adc = hasil_terakhir.get("kelembaban", 0)
    kelembaban_persen = hasil_terakhir.get("kelembaban_persen", 0)
    kelembaban_status = hasil_terakhir.get("kelembaban_status", "")

    # Simpan log ke DB tabel relay
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO relay (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, aksi, relay_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, aksi, 1 if manual_status else 0))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Gagal simpan log relay manual: {e}")
    
    try:
        from supabase_client import simpan_relay_log_supabase  # pastikan fungsi ini ada
        simpan_relay_log_supabase(
            ph=ph,
            ph_status=ph_status,
            kelembaban_adc=kelembaban_adc,
            kelembaban_persen=kelembaban_persen,
            kelembaban_status=kelembaban_status,
            durasi=durasi,
            aksi=aksi,
            relay_status=1 if manual_status else 0
        )
    except Exception as e:
        print(f"[ERROR] Gagal simpan log relay manual ke Supabase: {e}")

    return jsonify({"manual_mode": manual_mode, "relay_status": manual_status})

@app.route("/api/sensor", methods=["POST"])
def push_raw_sensor_ke_vps(ph_value, ph_label, kelembaban_adc, kelembaban_persen, kelembaban_label):
    payload = {
        "ph": ph_value,
        "ph_status": ph_label,
        "kelembaban_adc": kelembaban_adc,
        "kelembaban_persen": kelembaban_persen,
        "kelembaban_status": kelembaban_label,
        "waktu": datetime.now().isoformat()
    }
    try:
        res = requests.post("http://35.222.254.36:5000/api/sensor", json=payload, timeout=5)
        if res.status_code == 201:
            print("[VPS] Raw data sensor berhasil dikirim")
        else:
            print(f"[VPS] Gagal: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[VPS] Error kirim raw data: {e}")


if __name__ == "__main__":
    thread = threading.Thread(target=fuzzy_loop)
    thread.daemon = True
    thread.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
