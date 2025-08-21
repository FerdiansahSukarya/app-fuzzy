from supabase import create_client, Client
from datetime import datetime

# Ganti URL dan API Key sesuai kredensial
url = "https://siosiigonlauesjlafbq.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpb3NpaWdvbmxhdWVzamxhZmJxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTQ3ODUyMCwiZXhwIjoyMDY1MDU0NTIwfQ.7zdvu5Ltjr7J2SrHa4WmfFfxphmGxtTwHezvz1lEJpc"

supabase: Client = create_client(url, key)

def simpan_fuzzy_log_supabase(ph, status_ph, kelembaban, status_kelembaban, relay_status):
    """
    Simpan data log fuzzy ke tabel Supabase 'fuzzy_log'.
    Semua siklus tercatat, baik menyiram maupun tidak.
    """
    now = datetime.now().isoformat()

    data = {
        "waktu": now,
        "ph": ph,
        "status_ph": status_ph,
        "kelembaban": kelembaban,
        "status_kelembaban": status_kelembaban,
        "relay": relay_status,  # "ON" atau "OFF"
    }

    try:
        insert_response = supabase.table("fuzzy_log").insert(data).execute()
        if insert_response.data:
            print("[Supabase] Insert berhasil:", insert_response.data)
        else:
            print("[Supabase] Insert gagal atau tidak ada data tersimpan.")
    except Exception as e:
        print(f"[Supabase] Gagal insert data: {e}")
