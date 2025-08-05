# sensor_kelembaban.py

import serial
import threading
import time
import re

SERIAL_PORT = '/dev/ttyACM0'  # Ganti sesuai port Arduino kamu
BAUDRATE = 9600

latest_kelembaban = 0.0  # Dalam persen

def read_kelembaban():
    global latest_kelembaban
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"[INFO] Terhubung ke {SERIAL_PORT}")
        time.sleep(2)  # Tunggu serial siap

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # Contoh: "Nilai Analog: 840 | Kelembaban: 25% | Label: Kering"
                match = re.search(r'Kelembaban:\s*([0-9.]+)%', line)
                if match:
                    try:
                        kelembaban = float(match.group(1))
                        latest_kelembaban = round(kelembaban, 2)
                    except ValueError:
                        print("[WARNING] Gagal parsing angka kelembaban:", match.group(1))
                else:
                    print("[WARNING] Format tidak sesuai:", line)
            time.sleep(2)
    except serial.SerialException:
        print(f"[ERROR] Tidak bisa terhubung ke {SERIAL_PORT}. Cek koneksi USB Arduino.")

# Fungsi untuk Flask ambil nilai
def get_latest_kelembaban():
    return latest_kelembaban

# Jalankan thread saat file diimpor
thread = threading.Thread(target=read_kelembaban)
thread.daemon = True
thread.start()
