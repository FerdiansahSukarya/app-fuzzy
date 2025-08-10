import time
from relay_control import start_relay, stop_relay

def main_loop():
    while True:
        print("Nyalakan relay selama 15 detik...")
        start_relay()
        time.sleep(15)

        print("Matikan relay selama 45 detik...")
        stop_relay()
        time.sleep(45)

if __name__ == "__main__":
    main_loop()
