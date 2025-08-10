import RPi.GPIO as GPIO
import signal
import sys
import time

PIN_RELAY = 17  # Ganti sesuai GPIO kamu

def cleanup(signal_received, frame):
    GPIO.output(PIN_RELAY, GPIO.HIGH)
    GPIO.cleanup()
    print("Relay dimatikan, keluar program")
    sys.exit(0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_RELAY, GPIO.OUT)
GPIO.output(PIN_RELAY, GPIO.LOW)  # Relay ON (aktif LOW)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

print("Relay menyala. Tunggu perintah stop...")

while True:
    time.sleep(1)  # Tunggu sampai dihentikan oleh relay_control.py
