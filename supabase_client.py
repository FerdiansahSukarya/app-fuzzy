from supabase import create_client, Client
from datetime import datetime
import os

url = "https://siosiigonlauesjlafbq.supabase.co"  # Ganti sesuai milikmu
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpb3NpaWdvbmxhdWVzamxhZmJxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTQ3ODUyMCwiZXhwIjoyMDY1MDU0NTIwfQ.7zdvu5Ltjr7J2SrHa4WmfFfxphmGxtTwHezvz1lEJpc"
  # Ganti sesuai milikmu


supabase: Client = create_client(url, key)

def simpan_sensor_supabase(ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status):
    data = {
        "ph": ph,
        "ph_status": ph_status,
        "kelembaban_adc": kelembaban_adc,
        "kelembaban_persen": kelembaban_persen,
        "kelembaban_status": kelembaban_status
    }
    supabase.table("sensor").insert(data).execute()

def simpan_relay_supabase(ph, ph_status, kelembaban_adc, kelembaban_persen, kelembaban_status, durasi, aksi, relay_status):
    data = {
        "ph": ph,
        "ph_status": ph_status,
        "kelembaban_adc": kelembaban_adc,
        "kelembaban_persen": kelembaban_persen,
        "kelembaban_status": kelembaban_status,
        "durasi": durasi,
        "aksi": aksi,
        "relay_status": relay_status
    }
    supabase.table("relay").insert(data).execute()

def simpan_fuzzy_log_supabase(ph, ph_status, kelembaban, kelembaban_status, durasi, relay_status):
    now = datetime.now().isoformat()

    # Cek entri terakhir
    response = supabase.table("fuzzy_log") \
        .select("*") \
        .order("waktu", desc=True) \
        .limit(1) \
        .execute()

    if response.data:
        last = response.data[0]
        # Jika sama dan masih dalam 5 detik, skip
        if (
            last["ph"] == ph and
            last["kelembaban"] == kelembaban and
            last["durasi"] == durasi and
            last["relay_status"] == relay_status
        ):
            return  # Skip insert

    # Kirim data baru
    data = {
        "waktu": now,
        "ph": ph,
        "ph_status": ph_status,
        "kelembaban": kelembaban,
        "kelembaban_status": kelembaban_status,
        "durasi": durasi,
        "relay_status": relay_status
    }
    supabase.table("fuzzy_log").insert(data).execute()


