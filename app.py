from flask import Flask, render_template, jsonify, request
from fuzzy import evaluasi_fuzzy, siram_air
import threading
import time
from sensor_reader import baca_ph, baca_kelembaban
from relay_control import RelayControl
from supabase_client import simpan_fuzzy_log_supabase
from db import get_connection

app = Flask(__name__)
hasil_terakhir = {}
relay_ctrl = RelayControl()
manual_mode = False  # flag mode manual aktif atau tidak
manual_status = False  # status relay manual ON/OFF

def fuzzy_loop():
    global hasil_terakhir

    status_relay_sebelumnya = False  # False = OFF, True = ON

    while True:
        ph_value, ph_label = baca_ph()
        kelembaban_adc, kelembaban_persen, kelembaban_label = baca_kelembaban()

        hasil = evaluasi_fuzzy(ph_value, kelembaban_adc)  # fuzzy pakai ADC mentah
        hasil["ph_label"] = ph_label  
        hasil["kelembaban_persen"] = kelembaban_persen  # tambahkan persen untuk web
        hasil["kelembaban_status"] = kelembaban_label   # tambahkan label untuk web

        hasil_terakhir = hasil



        status_relay_saat_ini = hasil["durasi"] > 0

        # Jalankan penyiraman jika durasi > 0 (artinya jadwal + rule terpenuhi)
        if status_relay_saat_ini and not status_relay_sebelumnya:
            siram_air(hasil["durasi"])
            print(f"[RELAY] Menyiram {hasil['durasi']} detik")
        elif not status_relay_saat_ini and status_relay_sebelumnya:
            print("[RELAY] Tidak menyiram")

        # Hanya simpan ke Supabase jika status relay berubah
        if status_relay_saat_ini != status_relay_sebelumnya:
            simpan_fuzzy_log_supabase(
                hasil["ph"],
                hasil["ph_status"],
                hasil["kelembaban"],
                hasil["kelembaban_status"],
                hasil["durasi"],
                status_relay_saat_ini
            )
            print(f"[SUPABASE] Log disimpan (relay {'ON' if status_relay_saat_ini else 'OFF'})")

        status_relay_sebelumnya = status_relay_saat_ini

        time.sleep(10)  # Cek setiap 10 detik

@app.route("/riwayat")
def riwayat():
    return render_template("riwayat.html")

@app.route("/api/riwayat")
def api_riwayat():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM fuzzy_log ORDER BY waktu DESC LIMIT 30")
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
    else:
        stopped = relay_ctrl.stop_relay()
        manual_status = False

    return jsonify({"manual_mode": manual_mode, "relay_status": manual_status})

if __name__ == "__main__":
    thread = threading.Thread(target=fuzzy_loop)
    thread.daemon = True
    thread.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
