import time
from datetime import datetime, timedelta
import requests
from fuzzy import evaluasi_fuzzy, label_ph, label_kelembaban
from sensor_reader import baca_ph, baca_kelembaban
from relay_control import get_status_relay, start_relay, stop_relay
from supabase_client import simpan_fuzzy_log_supabase  # client Supabase sudah inisialisasi

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
    waktu_cek_fuzzy_berikutnya = datetime.now()

    while True:
        now = datetime.now()
        
        # Baca sensor
        ph_value, _ = baca_ph()
        kelembaban_adc, _, _ = baca_kelembaban()
        kelembaban_persen = max(0, min(100, round((1023 - kelembaban_adc) / 1023 * 100, 2)))

        # Label kondisi
        ph_status = label_ph(ph_value)
        kelembaban_status = label_kelembaban(kelembaban_adc)

        # Jalankan fuzzy tiap 1 jam
        if now >= waktu_cek_fuzzy_berikutnya:
            hasil_fuzzy = evaluasi_fuzzy(ph_value, kelembaban_adc)
            durasi_siram = hasil_fuzzy.get("durasi", 0)

            if durasi_siram > 0:
                if start_relay():
                    print(f"[RELAY] Menyiram selama {durasi_siram} detik...")
                    selesai = time.monotonic() + durasi_siram

                    while time.monotonic() < selesai and get_status_relay():
                        # Baca ulang sensor setiap detik
                        ph_now, _ = baca_ph()
                        adc_now, _, _ = baca_kelembaban()
                        persen_now = max(0, min(100, round((1023 - adc_now) / 1023 * 100, 2)))

                        realtime_payload = {
                            "ph": ph_now,
                            "ph_status": label_ph(ph_now),
                            "kelembaban_adc": adc_now,
                            "kelembaban_persen": persen_now,
                            "kelembaban_status": label_kelembaban(adc_now),
                            "status_relay": "ON",
                            "waktu": datetime.now().isoformat()
                        }
                        kirim_ke_vps(realtime_payload)
                        time.sleep(1)

                    stop_relay()
                relay_val = 1
            else:
                stop_relay()
                relay_val = 0

            # Simpan log ke Supabase
            simpan_fuzzy_log_supabase(
                ph_value,
                ph_status,
                kelembaban_persen,
                kelembaban_status,
                relay_val
            )

            waktu_cek_fuzzy_berikutnya = now + timedelta(seconds=3600)

        # Update status relay terbaru (jika tidak sedang fuzzy)
        status_relay = "ON" if get_status_relay() else "OFF"

        # Kirim realtime ke VPS (sensor terbaru)
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

        time.sleep(1)

if __name__ == "__main__":
    main_loop()
