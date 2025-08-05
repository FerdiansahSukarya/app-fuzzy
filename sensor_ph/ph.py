import smbus2 as smbus
import time
import threading  # Import modul threading

bus = smbus.SMBus(1)
address = 0x04

def read_ph():
    while True:
        try:
            data = bus.read_i2c_block_data(address, 0, 6)  # Membaca 6 byte
            pH = (data[4] << 8) | data[5]
            pH /= 100.0
            print("pH: {:.1f}".format(pH))
        except OSError as e:
            print("Kesalahan I2C:", str(e))
        time.sleep(5)

ph_thread = threading.Thread(target=read_ph)
ph_thread.daemon = True
ph_thread.start()

try:
    while True:
        # Tempatkan tugas-tugas utama Anda di sini
        time.sleep(1)
except KeyboardInterrupt:
    print("Keluar dari program.")
