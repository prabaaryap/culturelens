from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from .users import get_current_user
from db import models
import numpy as np
from PIL import Image
import io
import tensorflow as tf

router = APIRouter(prefix="/detection", tags=["Detection"])

# ==========================================
# 1. DATABASE DESKRIPSI (Updated)
# ==========================================
# Kunci (Key) harus SAMA PERSIS (huruf besar/kecil) dengan LABELS di bawah
OBJECT_DATABASE = {
    "Canang": {
        "about": "Canang Sari adalah persembahan harian umat Hindu Bali yang terbuat dari janur dan bunga. Ini melambangkan rasa syukur kepada Sang Hyang Widhi Wasa.",
        "donts": [
            "Jangan melangkahi Canang yang baru diletakkan",
            "Jangan menginjak dengan sengaja"
        ]
    },
    "Kwangen": {
        "about": "Kwangen adalah sarana persembahyangan yang terbuat dari janur, bunga, dan uang kepeng. Sering digunakan dalam sembahyang panca sembah.",
        "donts": [
            "Jangan membuang sembarangan setelah dipakai sembahyang",
            "Gunakan dengan tangan kanan saat berdoa"
        ]
    },
    "Pelangkiran": {
        "about": "Pelangkiran adalah tempat suci kecil yang biasanya ditempatkan di kamar tidur, warung, atau kantor sebagai tempat berstananya Dewa pelindung.",
        "donts": [
            "Jangan menaruh barang kotor atau tidak pantas di atasnya",
            "Jangan menunjuk pelangkiran dengan kaki"
        ]
    },
    "Penjor": {
        "about": "Penjor adalah bambu melengkung yang dihias janur, dipasang di depan rumah saat Galungan. Ini melambangkan Gunung Agung dan Naga Basuki.",
        "donts": [
            "Jangan menarik atau merusak hiasan Penjor",
            "Hormati sebagai simbol kemenangan Dharma melawan Adharma"
        ]
    },
    "Sanggah Cucuk": {
        "about": "Sanggah Cucuk adalah tempat persembahan sederhana berbentuk segitiga dari bambu, sering digunakan untuk upacara Pecaruan (pembersihan roh jahat).",
        "donts": [
            "Jangan mengganggu sesajen di dalamnya",
            "Biasanya diletakkan di pintu masuk atau perempatan jalan, harap berhati-hati saat lewat"
        ]
    },
    "banten": { # Huruf 'b' kecil sesuai label Anda
        "about": "Banten adalah istilah umum untuk persembahan atau sesajen dalam upacara Hindu Bali yang lebih kompleks daripada Canang.",
        "donts": [
            "Jangan mengambil makanan/buah (lungsuran) sebelum upacara selesai",
            "Jangan menyentuh saat Pemangku sedang mendoakannya"
        ]
    },
    "pelinggih": { # Huruf 'p' kecil sesuai label Anda
        "about": "Pelinggih adalah bangunan suci (takhta) tempat berstananya Dewa atau leluhur di Pura atau Sanggah (tempat suci keluarga).",
        "donts": [
            "Dilarang memanjat atau duduk di atas Pelinggih",
            "Wanita yang sedang haid dilarang masuk area utama (Mandala Utama)",
            "Jaga kesopanan bicara dan perilaku di area ini"
        ]
    }
}

# ==========================================
# 2. KONFIGURASI MODEL LOKAL
# ==========================================
MODEL_PATH = "MobileNetV2.h5" 
MODEL = None

# PENTING: URUTAN INI HARUS SAMA PERSIS DENGAN 'class_names' DI NOTEBOOK TRAINING ANDA
LABELS = [
    'Canang', 
    'Kwangen', 
    'Pelangkiran', 
    'Penjor', 
    'Sanggah Cucuk', 
    'banten', 
    'pelinggih'
]

# Load Model saat aplikasi mulai (Hanya sekali agar cepat)
try:
    print(f"Sedang memuat model dari {MODEL_PATH}...")
    MODEL = tf.keras.models.load_model(MODEL_PATH)
    print("Model berhasil dimuat!")
except Exception as e:
    print(f"FATAL: Gagal memuat model: {e}")

def predict_local(image_bytes):
    if MODEL is None:
        return None, 0.0
    
    try:
        # --- Pre-processing Gambar ---
        # 1. Buka gambar dari bytes & konversi ke RGB (hilangkan Alpha channel jika PNG)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # 2. Resize sesuai input model MobileNetV2 (224x224)
        image = image.resize((224, 224)) 
        
        # 3. Ubah ke array numpy
        img_array = np.array(image)
        
        # 4. Tambah dimensi batch (Model butuh input [1, 224, 224, 3])
        img_array = np.expand_dims(img_array, axis=0) 
        
        # 5. Normalisasi (Ubah nilai pixel 0-255 menjadi 0-1)
        # PENTING: Pastikan training Anda juga melakukan pembagian 255.0 ini. 
        # Jika training Anda tidak membagi 255, hapus baris ini.
        img_array = img_array / 255.0

        # --- Prediksi ---
        predictions = MODEL.predict(img_array)
        score = tf.nn.softmax(predictions[0]) # Hitung probabilitas
        
        class_index = np.argmax(score) # Ambil index dengan nilai tertinggi
        confidence = 100 * np.max(score) # Ambil persentase keyakinan
        
        # Ambil nama label berdasarkan index urutan
        detected_label = LABELS[class_index]
        
        return detected_label, confidence
        
    except Exception as e:
        print(f"Error saat prediksi: {e}")
        return None, 0.0

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Baca file gambar
    image_bytes = await file.read()
    
    # 2. Proses dengan Model Lokal
    detected_label, confidence = predict_local(image_bytes)
    
    if detected_label is None:
        raise HTTPException(status_code=500, detail="Gagal memproses gambar pada server")

    # 3. Ambil Detail dari Database Lokal
    # Gunakan .get() agar tidak error jika label tidak ditemukan
    object_info = OBJECT_DATABASE.get(detected_label, {
        "about": f"Objek terdeteksi sebagai {detected_label}, namun deskripsi detail belum tersedia.",
        "donts": ["Harap menjaga kesopanan dan menghormati budaya setempat"]
    })

    # 4. Kembalikan Hasil JSON
    return {
        "object_name": detected_label,
        "accuracy": float(confidence), # Float agar kompatibel dengan JSON
        "about": object_info["about"],
        "donts": object_info["donts"]
    }