import RPi.GPIO as GPIO

# Konfigurasi GPIO
RELAY_PIN = 17  # Ganti sesuai pin GPIO yang kamu pakai
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

try:
    print("Pompa hidup (relay ON)...")
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay aktif (ON)
    input("Tekan Enter untuk mematikan pompa...")  # Tunggu input user
    GPIO.output(RELAY_PIN, GPIO.HIGH) # Relay mati (OFF)
    print("Pompa dimatikan.")
except KeyboardInterrupt:
    print("Dihentikan oleh pengguna.")
finally:
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    GPIO.cleanup()
