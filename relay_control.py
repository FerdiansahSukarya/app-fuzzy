# relay_control.py

import time
import threading
import subprocess

relay_status = {
    "aktif": False,
    "waktu_mulai": None,
    "durasi": 0
}

def siram_air(durasi_detik):
    if relay_status["aktif"]:
        print("[RELAY CONTROL] Relay sedang aktif, abaikan perintah baru.")
        return

    def tugas():
        print(f"[RELAY CONTROL] Menyalakan relay selama {durasi_detik} detik")
        relay_status["aktif"] = True
        relay_status["waktu_mulai"] = time.time()
        relay_status["durasi"] = durasi_detik

        subprocess.run(["python3", "relay.py"])  # ?? NYALAKAN RELAY
        time.sleep(durasi_detik)
        subprocess.run(["python3", "matikan_gpio.py"])  # ? MATIKAN RELAY

        relay_status["aktif"] = False
        relay_status["waktu_mulai"] = None
        relay_status["durasi"] = 0
        print("[RELAY CONTROL] Relay dimatikan")

    thread = threading.Thread(target=tugas)
    thread.daemon = True
    thread.start()

def get_status_relay():
    return relay_status.copy()
