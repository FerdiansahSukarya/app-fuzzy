import threading
import time
from relay_control import start_relay, stop_relay
from supabase_client import simpan_fuzzy_log_supabase


def label_ph(ph):
    if ph < 4.4:
        return "Sangat Masam"
    elif 4.4 <= ph <= 5.6:
        return "Masam"
    elif 5.6 < ph <= 6.5:
        return "Sedikit Masam"
    elif 6.5 < ph <= 7.5:
        return "Netral"
    elif ph > 7.5:
        return "Basa"
    else:
        return "Tidak Terdefinisi"

def label_kelembaban(adc):
    if adc > 800:
        return "Kering"
    elif adc > 400:
        return "Lembab"
    else:
        return "Basah"

def fuzzy_rules(ph_label, kelembaban_label):
    siram_conditions = {
        ("Sangat Masam", "Kering"),
        ("Masam", "Kering"),
        ("Sedikit Masam", "Kering"),
        ("Netral", "Kering"),
        ("Basa", "Kering"),

        ("Sangat Masam", "Lembab"),
        ("Masam", "Lembab"),
        ("Sedikit Masam", "Lembab"),
        ("Netral", "Lembab"),
        ("Basa", "Lembab"),
    }
    if (ph_label, kelembaban_label) in siram_conditions:
        return 900
    else:
        return 0

def siram_air(durasi):
    def worker():
        if start_relay():
            print(f"Relay ON selama {durasi} detik")
            time.sleep(durasi)
            stop_relay()
            print("Relay OFF setelah durasi")
        else:
            print("Relay sudah ON, tidak menyalakan ulang")
    threading.Thread(target=worker, daemon=True).start()

def evaluasi_fuzzy(ph, kelembaban_adc):
    try:
        # Label kondisi
        ph_status = label_ph(ph)
        kelembaban_status = label_kelembaban(kelembaban_adc)
        kelembaban_persen = max(0, min(100, round((1023 - kelembaban_adc) / 1023 * 100, 2)))

        # Evaluasi aturan fuzzy
        durasi = fuzzy_rules(ph_status, kelembaban_status)

        # Simpan log evaluasi ke Supabase
        simpan_fuzzy_log_supabase(
            ph,
            ph_status,
            kelembaban_persen,
            kelembaban_status,
            1 if durasi > 0 else 0
        )

        # Return hasil evaluasi
        return {
            "ph": ph,
            "ph_status": ph_status,
            "kelembaban": kelembaban_adc,
            "kelembaban_persen": kelembaban_persen,
            "kelembaban_status": kelembaban_status,
            "durasi": durasi
        }

    except Exception as e:
        print(f"[ERROR] evaluasi_fuzzy gagal: {e}")
        # Tetap return dictionary default agar loop utama tidak error
        return {
            "ph": ph,
            "ph_status": "Error",
            "kelembaban": kelembaban_adc,
            "kelembaban_persen": 0,
            "kelembaban_status": "Error",
            "durasi": 0
        }

