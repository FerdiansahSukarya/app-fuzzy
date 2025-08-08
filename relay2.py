import RPi.GPIO as GPIO
import time

# Konfigurasi
PWM_PIN = 17
PWM_FREQ = 100  # Hz
DUTY_CYCLE = 8  # untuk mencapai sekitar 20 RPM (berdasarkan uji DP-DIY)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)

# Mulai PWM
pwm = GPIO.PWM(PWM_PIN, PWM_FREQ)
pwm.start(DUTY_CYCLE)

try:
    print("Pompa berjalan pada 20 RPM...")
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Pompa dimatikan.")
    pwm.stop()
    GPIO.cleanup()
