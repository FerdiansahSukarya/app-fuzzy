# raspberry_pi_upload.py
import requests

data = {
    "ph": 6.3,
    "kelembaban": 40
}
try:
    response = requests.post("https://35.222.254.36/api/sensor", json=data)
    print("Data dikirim ke VPS:", response.text)
except Exception as e:
    print("Gagal:", e)
