# fuzzy.py

from relay_control import siram_air
import time

# JEDA antar penyiraman (dalam detik)
JEDA_WAKTU = 60  # 1 menit (ubah sesuai kebutuhan)

# Variabel global untuk menyimpan waktu penyiraman terakhir
last_siram_time = 0

def label_ph(ph):
    if ph < 4.5:
        return "Agak Masam"
    elif 4.5 <= ph <= 4.9:
        return "Masam"
    elif 5.0 <= ph <= 6.5:
        return "Netral"
    else:
        return "Netral"  # fallback jika > 6.5

def label_kelembaban(persen):
    if persen < 30:
        return "Kering"
    elif persen <= 69:
        return "Cukup"
    else:
        return "Basah"

def fuzzy_rules(ph_label, kelembaban_label):

    rules = {
        ("Asam", "Kering"): 20,
        ("Asam", "Cukup"): 10,
        ("Asam", "Basah"): 5,
        ("Netral", "Kering"): 20,
        ("Netral", "Cukup"): 10,
        ("Netral", "Basah"): 5,
        ("Basa", "Kering"): 10,
        ("Basa", "Cukup"): 5,
        ("Basa", "Basah"): 0,
    }
    return rules.get((ph_label, kelembaban_label), 0)

def evaluasi_fuzzy(ph, kelembaban):
    global last_siram_time

    ph_status = label_ph(ph)
    kelembaban_status = label_kelembaban(kelembaban)

    durasi = fuzzy_rules(ph_status, kelembaban_status)

    print(f"[FUZZY] pH: {ph} -> {ph_status}, Kelembaban: {kelembaban}% -> {kelembaban_status}")
    print(f"[FUZZY] Hasil: Siram selama {durasi} detik")

    sekarang = time.time()
    waktu_sejak_terakhir_siram = sekarang - last_siram_time

    if durasi > 0:
        if waktu_sejak_terakhir_siram >= JEDA_WAKTU:
            print("[FUZZY] Menyiram karena sudah lewat jeda")
            siram_air(durasi)
            last_siram_time = sekarang
        else:
            print(f"[FUZZY] Dilewati karena jeda belum cukup: {waktu_sejak_terakhir_siram:.1f}s")
    else:
        print("[FUZZY] Tidak perlu menyiram (durasi 0)")

    return {
        "ph": ph,
        "ph_status": ph_status,
        "kelembaban": kelembaban,
        "kelembaban_status": kelembaban_status,
        "durasi": durasi
    }

