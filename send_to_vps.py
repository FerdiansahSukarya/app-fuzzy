import time
from datetime import datetime, timedelta
import requests
from fuzzy import evaluasi_fuzzy, siram_air, label_ph, label_kelembaban
from sensor_reader import baca_ph, baca_kelembaban
from relay_control import get_status_relay

VPS_URL = "http://35.222.254.36:5000/api/sensor"

def kirim_ke_vps(data):
    try:
        res = requests.post(VPS_URL, json=data, timeout=5)
        print(f"[VPS DEBUG] Status: {res.status_code}, Response: {res.text}")
        if res.status_code in (200, 201):
            print(f"[VPS] Data terkirim: {data}")
        else:
            print(f"[VPS] Gagal kirim: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[ERROR] Gagal kirim data ke VPS: {e}")

def main_loop():
    fuzzy_nonaktif_sampai = None
    waktu_cek_fuzzy_berikutnya = datetime.now()

    while True:
        now = datetime.now()
        ph_value, _ = baca_ph()
        kelembaban_adc, _, _ = baca_kelembaban()
        kelembaban_persen = max(0, min(100, round((1023 - kelembaban_adc) / 1023 * 100, 2)))

        ph_status = label_ph(ph_value)
        kelembaban_status = label_kelembaban(kelembaban_adc)
        status_relay = "ON" if get_status_relay() else "OFF"

        realtime_payload = {
            "ph": ph_value,
            "ph_status": ph_status,
            "kelembaban_adc": kelembaban_adc,
            "kelembaban_persen": kelembaban_persen,
            "kelembaban_status": kelembaban_status,
            "status_relay": status_relay,
            "waktu": now.isoformat()
        }

        kirim_ke_vps(realtime_payload)

        if now >= waktu_cek_fuzzy_berikutnya and (fuzzy_nonaktif_sampai is None or now >= fuzzy_nonaktif_sampai):
            hasil = evaluasi_fuzzy(ph_value, kelembaban_adc)

            if hasil["durasi"] > 0:
                print(f"[MAIN] Relay AKTIF selama {hasil['durasi']} detik")
                siram_air(hasil["durasi"])

                fuzzy_nonaktif_sampai = datetime.now() + timedelta(seconds=hasil["durasi"] + 45)
            else:
                print("[MAIN] Tidak siram")

            waktu_cek_fuzzy_berikutnya = now + timedelta(seconds=60)

        time.sleep(1)


if __name__ == "__main__":
    main_loop()
