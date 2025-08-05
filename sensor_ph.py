# sensor_ph.py

import smbus2 as smbus
import time
import threading

bus = smbus.SMBus(1)
address = 0x04

# Variabel global untuk menyimpan nilai pH terbaru
latest_ph = 0.0

def read_ph():
    global latest_ph
    while True:
        try:
            data = bus.read_i2c_block_data(address, 0, 6)  # Membaca 6 byte
            ph = (data[4] << 8) | data[5]
            ph /= 100.0
            latest_ph = round(ph, 2)
        except OSError as e:
            print("Kesalahan I2C:", str(e))
            latest_ph = 0.0
        time.sleep(5)  # Delay 5 detik

# Fungsi untuk diakses oleh Flask
def get_latest_ph():
    return latest_ph

# Mulai thread saat modul diimpor
ph_thread = threading.Thread(target=read_ph)
ph_thread.daemon = True
ph_thread.start()
