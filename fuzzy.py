import threading
import time
from relay_control import start_relay, stop_relay
from database import simpan_relay_mysql
from supabase_client import simpan_relay_supabase

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

# Aturan fuzzy berdasarkan R1-R15:
# Jika perlu siram, durasi siram 15 detik, jika tidak perlu siram durasi 0
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
        return 15
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
    ph_status = label_ph(ph)
    kelembaban_status = label_kelembaban(kelembaban_adc)
    kelembaban_persen = max(0, min(100, round((1023 - kelembaban_adc) / 1023 * 100, 2)))

    durasi = fuzzy_rules(ph_status, kelembaban_status)

    if durasi > 0:
        print(f"[FUZZY] Aturan mengatakan SIRAM selama {durasi} detik (pH: {ph_status}, Kelembaban: {kelembaban_status})")
        siram_air(durasi)
        simpan_relay_mysql(ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, "SIRAM", 1)
        simpan_relay_supabase(ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, "SIRAM", 1)
    else:
        print(f"[FUZZY] Aturan mengatakan TIDAK SIRAM (pH: {ph_status}, Kelembaban: {kelembaban_status})")
        simpan_relay_mysql(ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, 0, "TIDAK SIRAM", 0)
        simpan_relay_supabase(ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, 0, "TIDAK SIRAM", 0)

    return {
        "ph": ph,
        "ph_status": ph_status,
        "kelembaban_adc": kelembaban_adc,
        "kelembaban_persen": kelembaban_persen,
        "kelembaban_status": kelembaban_status,
        "durasi": durasi
    }
