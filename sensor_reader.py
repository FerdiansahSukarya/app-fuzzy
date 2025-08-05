# sensor_reader.py

import smbus2 as smbus
import serial
import time

# --- I2C pH SENSOR ---
bus = smbus.SMBus(1)
address = 0x04

def baca_ph():
    try:
        data = bus.read_i2c_block_data(address, 0, 6)
        ph = (data[4] << 8) | data[5]
        ph = ph / 100.0
        return round(ph, 2)
    except:
        return 0.0  # fallback jika error

# --- SERIAL KELEMBABAN DARI ARDUINO ---
# Pastikan port sesuai dengan yang terhubung ke Arduino, misal: /dev/ttyUSB0 atau /dev/ttyACM0
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)  # beri waktu serial connect
except:
    ser = None

def baca_kelembaban():
    if ser and ser.in_waiting:
        try:
            line = ser.readline().decode().strip()
            if "Kelembaban:" in line:
                persen = int(line.split("Kelembaban:")[1].split("%")[0].strip())
                return persen
        except:
            pass
    return 0  # fallback
