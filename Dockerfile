# 1. Base Image: Gunakan image Python 3.10 yang ringan
FROM python:3.10-slim

# 2. Set Working Directory: Buat folder /app di dalam container
WORKDIR /app

# 3. Salin & Install Dependencies: 
#    Salin requirements.txt dulu agar Docker bisa cache
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. Salin Kode Aplikasi Anda:
#    Salin semua file dan folder (seperti /core, /db, /routers, dll) ke /app
COPY . .

# 5. Jalankan Aplikasi:
#    Perintahkan uvicorn untuk menjalankan 'app' dari file 'main.py'
#    Ini akan berjalan di port 8080, yang dideteksi otomatis oleh Cloud Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]