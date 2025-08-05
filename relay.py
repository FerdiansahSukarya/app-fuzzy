# relay.py

import RPi.GPIO as GPIO

RELAY_PIN = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Aktifkan relay

print("[RELAY] Relay DINYALAKAN.")
