import smbus2 as smbus
import serial
import time

# --- I2C pH SENSOR ---
bus = smbus.SMBus(1)
address = 0x04

def baca_ph():
    """Baca nilai pH dari sensor pH via I2C."""
    try:
        data = bus.read_i2c_block_data(address, 0, 6)
        ph = (data[4] << 8) | data[5]
        ph = ph / 100.0
        return round(ph, 2), label_ph(ph)
    except Exception as e:
        print(f"[ERROR] Gagal baca pH: {e}")
        return 0.0, "Tidak Terbaca"

def label_ph(ph):
    """Konversi nilai pH menjadi label sesuai dokumen."""
    if ph < 4.4:
        return "Sangat Masam"
    elif 4.4 <= ph <= 5.6:
        return "Masam"
    elif 5.6 < ph <= 6.5:
        return "Sedikit Masam"
    elif 6.5 < ph <= 7.5:
        return "Netral"
    else:
        return "Basa"
    
    
# --- SERIAL KELEMBABAN DARI ARDUINO ---
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)  # beri waktu serial connect
    print("[INFO] Terhubung ke Arduino di /dev/ttyACM0")
except Exception as e:
    print(f"[ERROR] Tidak bisa terhubung ke Arduino: {e}")
    ser = None

def label_kelembaban(nilai_adc):
    """Konversi nilai ADC ke label kelembaban sesuai dokumen."""
    if nilai_adc > 450:
        return "Kering"
    elif nilai_adc > 350:
        return "Lembab"
    else:
        return "Basah"

def adc_ke_persen(nilai_adc):
    """Konversi nilai ADC ke persen kelembaban."""
    # Rumus: ADC tinggi = kering, ADC rendah = basah
    return round((1023 - nilai_adc) / 1023 * 100, 2)

def baca_kelembaban():
    """
    Baca nilai kelembaban dari Arduino.
    Return: (nilai_adc, persen, label)
    """
    if ser and ser.in_waiting:
        try:
            line = ser.readline().decode().strip()
            if line.isdigit():
                nilai_adc = int(line)
                persen = adc_ke_persen(nilai_adc)
                return nilai_adc, persen, label_kelembaban(nilai_adc)
        except Exception as e:
            print(f"[ERROR] Gagal baca kelembaban: {e}")
    return 0, 0.0, "Tidak Terbaca"
