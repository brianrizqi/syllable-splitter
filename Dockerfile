# Menggunakan base image Python yang ringan
FROM python:3.12-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Menyalin file requirements.txt
COPY requirements.txt .

# Menginstal dependensi aplikasi dan gunicorn (untuk server production)
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Menyalin seluruh file proyek ke dalam container
COPY . .

# Mengekspose port 8000 (port yang akan digunakan gunicorn)
EXPOSE 8000

# Menentukan instruksi untuk menjalankan aplikasi menggunakan Gunicorn
# app:app merujuk ke nama file app.py dan variabel `app = Flask(__name__)`
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "app:app"]
