import subprocess
import threading

process = None
lock = threading.Lock()

def start_relay():
    global process
    with lock:
        if process is not None and process.poll() is None:
            print("Relay sudah ON, tidak menyalakan ulang")
            return False
        process = subprocess.Popen(["python3", "relay.py"])
        print("Relay menyala (relay.py dijalankan)")
        return True

def stop_relay():
    global process
    with lock:
        if process is None or process.poll() is not None:
            print("Relay sudah OFF, tidak menonaktifkan ulang")
            return False
        process.terminate()
        process.wait()
        process = None
        print("Relay mati (proses relay.py dihentikan)")
        return True

def get_status_relay():
    """Mengembalikan True jika relay.py sedang berjalan, False jika tidak."""
    global process
    with lock:
        return process is not None and process.poll() is None
