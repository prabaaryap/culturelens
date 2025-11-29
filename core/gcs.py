import os
from google.cloud import storage
import uuid

# Ganti dengan nama bucket yang Anda buat di Langkah 1
BUCKET_NAME = "culturelens-uploads-2025" 

def upload_image_to_gcs(file, filename: str, content_type: str) -> str:
    """
    Mengupload file ke Google Cloud Storage dan mengembalikan URL publiknya.
    """
    try:
        # 1. Inisialisasi Client (Otomatis pakai kredensial Cloud Run)
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        # 2. Buat nama file unik agar tidak bentrok
        # Contoh: images/a1b2c3d4-foto.jpg
        unique_filename = f"images/{uuid.uuid4()}-{filename}"
        blob = bucket.blob(unique_filename)

        # 3. Upload file
        # file.file adalah objek file dari UploadFile FastAPI
        blob.upload_from_file(file.file, content_type=content_type)

        # 4. Kembalikan URL Publik
        # Karena kita sudah set bucket jadi public, URL ini bisa langsung dibuka
        return blob.public_url

    except Exception as e:
        print(f"Gagal upload ke GCS: {e}")
        raise e