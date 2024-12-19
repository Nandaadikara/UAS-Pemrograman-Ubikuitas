from flask import Flask, jsonify
from flask_cors import CORS
import requests
import firebase_admin
from firebase_admin import credentials
from apscheduler.schedulers.background import BackgroundScheduler

# Inisialisasi Firebase Admin SDK dengan kredensial JSON
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)
CORS(app)

# URL Realtime Database Firebase
FIREBASE_URL = "https://uts-integrasi-data-senso-fee8c-default-rtdb.asia-southeast1.firebasedatabase.app/sensor_data.json"

# Variabel global untuk menyimpan data terbaru
global_data = {
    'kecepatan_angin': 0.0,
    'kelembaban': 0.0,
    'suhu': 0.0,
    'status_keamanan': "Tidak Diketahui"
}

# Fungsi untuk mendapatkan data dari Firebase
def get_data_from_firebase():
    try:
        response = requests.get(FIREBASE_URL)
        response.raise_for_status()
        data = response.json()

        # Memastikan data yang diterima dalam format yang benar
        wind_speed = float(data.get('kecepatan_angin', 0.0))
        humidity = float(data.get('kelembaban', 0.0))
        temperature = float(data.get('suhu', 0.0))

        return {
            'kecepatan_angin': wind_speed,
            'kelembaban': humidity,
            'suhu': temperature
        }

    except Exception as e:
        print(f"Error fetching data from Firebase: {e}")
        return {
            'kecepatan_angin': 0.0,
            'kelembaban': 0.0,
            'suhu': 0.0
        }

# Fungsi untuk menentukan status keamanan jalur
def classify_safety(wind_speed, humidity, temperature):
    """
    Aturan klasifikasi keamanan:
    1. Jika kecepatan angin > 10 m/s -> Berbahaya (Angin Kencang)
    2. Jika suhu < 20°C -> Berbahaya (Suhu Dingin)
    3. Jika kelembaban > 85% + suhu < 20°C -> Berbahaya (Kondisi Lembab dan Dingin)
    4. Jika kelembaban > 85% + suhu < 20°C + kecepatan angin > 10 m/s -> Berbahaya (Kondisi Ekstrem)
    5. Selain kondisi di atas -> Aman
    """
    if wind_speed > 18:
        return "Berbahaya (Angin Kencang)"
    elif temperature < 25:
        return "Berbahaya (Suhu Dingin)"
    elif humidity > 85 and temperature < 25:
        return "Berbahaya (Berkabut)"
    elif humidity > 85 and temperature < 25 and wind_speed > 10:
        return "Berbahaya (Kondisi Ekstrem)"
    else:
        return "Aman"

# Fungsi untuk memperbarui data global
def update_global_data():
    global global_data

    # Ambil data dari Firebase
    data = get_data_from_firebase()

    # Tentukan status keamanan jalur
    safety_status = classify_safety(data['kecepatan_angin'], data['kelembaban'], data['suhu'])

    # Perbarui data global
    global_data = {
        'kecepatan_angin': data['kecepatan_angin'],
        'kelembaban': data['kelembaban'],
        'suhu': data['suhu'],
        'status_keamanan': safety_status
    }
    print("Global data updated:", global_data)

# Jalankan pembaruan data setiap 1 menit
scheduler = BackgroundScheduler()
scheduler.add_job(update_global_data, 'interval', minutes=1)
scheduler.start()

# Route untuk menampilkan pesan dasar
@app.route('/')
def home():
    return "API is running. Use /getSensorData to fetch data."

# Route untuk mengambil data sensor dari global data
@app.route('/getSensorData', methods=['GET'])
def get_sensor_data():
    return jsonify(global_data)

if __name__ == '__main__':
    # Pastikan thread scheduler berhenti saat aplikasi dihentikan
    try:
        update_global_data()  # Perbarui data saat server pertama kali dijalankan
        app.run(debug=True)
    finally:
        scheduler.shutdown()
