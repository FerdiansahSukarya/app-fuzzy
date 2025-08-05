# app.py

from flask import Flask, render_template, jsonify
from fuzzy import evaluasi_fuzzy
import threading
import time
from relay_control import siram_air, get_status_relay
from sensor_reader import baca_ph, baca_kelembaban

siram_air(10)

app = Flask(__name__)

# Variabel global hasil fuzzy terakhir
hasil_terakhir = {}

# Jalankan evaluasi fuzzy tiap 5 detik di background
def fuzzy_loop():
    global hasil_terakhir
    while True:
        hasil_terakhir = evaluasi_fuzzy()
        time.sleep(5)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    ph = baca_ph()
    kelembaban = baca_kelembaban()
    hasil = evaluasi_fuzzy(ph, kelembaban)
    hasil["relay"] = get_status_relay()
    return jsonify(hasil)

if __name__ == "__main__":
    # Mulai thread fuzzy
    thread = threading.Thread(target=fuzzy_loop)
    thread.daemon = True
    thread.start()

    # Jalankan Flask (lokal)
    app.run(host="0.0.0.0", port=5000, debug=True)
