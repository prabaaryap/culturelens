from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from .users import get_current_user
from db import models
from enum import Enum

# --- IMPORT PENTING ---
# Kita memanggil fungsi dari file ml.py yang baru kita buat di atas
from core.ml import predict_object 

router = APIRouter(prefix="/detection", tags=["Detection"])

# Enum untuk pilihan dropdown di Swagger UI
class ModelChoice(str, Enum):
    mobilenet = "mobilenet"
    efficientnet = "efficientnet"

# ==========================================
# DATABASE DESKRIPSI (Tidak Berubah)
# ==========================================
OBJECT_DATABASE = {
    "Canang": {
        "about": "Canang Sari adalah persembahan harian umat Hindu Bali yang terbuat dari janur dan bunga. Ini melambangkan rasa syukur kepada Sang Hyang Widhi Wasa.",
        "donts": ["Jangan melangkahi Canang yang baru diletakkan", "Jangan menginjak dengan sengaja"]
    },
    "Kwangen": {
        "about": "Kwangen adalah sarana persembahyangan yang terbuat dari janur, bunga, dan uang kepeng. Sering digunakan dalam sembahyang panca sembah.",
        "donts": ["Jangan membuang sembarangan setelah dipakai sembahyang", "Gunakan dengan tangan kanan saat berdoa"]
    },
    "Pelangkiran": {
        "about": "Pelangkiran adalah tempat suci kecil yang biasanya ditempatkan di kamar tidur, warung, atau kantor sebagai tempat berstananya Dewa pelindung.",
        "donts": ["Jangan menaruh barang kotor atau tidak pantas di atasnya", "Jangan menunjuk pelangkiran dengan kaki"]
    },
    "Penjor": {
        "about": "Penjor adalah bambu melengkung yang dihias janur, dipasang di depan rumah saat Galungan. Ini melambangkan Gunung Agung dan Naga Basuki.",
        "donts": ["Jangan menarik atau merusak hiasan Penjor", "Hormati sebagai simbol kemenangan Dharma melawan Adharma"]
    },
    "Sanggah Cucuk": {
        "about": "Sanggah Cucuk adalah tempat persembahan sederhana berbentuk segitiga dari bambu, sering digunakan untuk upacara Pecaruan (pembersihan roh jahat).",
        "donts": ["Jangan mengganggu sesajen di dalamnya", "Biasanya diletakkan di pintu masuk atau perempatan jalan, harap berhati-hati saat lewat"]
    },
    "banten": {
        "about": "Banten adalah istilah umum untuk persembahan atau sesajen dalam upacara Hindu Bali yang lebih kompleks daripada Canang.",
        "donts": ["Jangan mengambil makanan/buah (lungsuran) sebelum upacara selesai", "Jangan menyentuh saat Pemangku sedang mendoakannya"]
    },
    "pelinggih": {
        "about": "Pelinggih adalah bangunan suci (takhta) tempat berstananya Dewa atau leluhur di Pura atau Sanggah (tempat suci keluarga).",
        "donts": ["Dilarang memanjat atau duduk di atas Pelinggih", "Wanita yang sedang haid dilarang masuk area utama (Mandala Utama)", "Jaga kesopanan bicara dan perilaku di area ini"]
    }
}

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    # Parameter baru: User bisa memilih model (Default: Mobilenet)
    model_type: ModelChoice = Query(ModelChoice.mobilenet, description="Pilih model: 'mobilenet' (Ringan) atau 'efficientnet' (Akurat)"),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Baca file gambar
    image_bytes = await file.read()
    
    # 2. Panggil fungsi prediksi dari core/ml.py
    # Kita kirimkan pilihan model dari user (model_type.value) ke fungsi tersebut
    try:
        detected_label, confidence = predict_object(image_bytes, model_type.value)
    except ValueError as e:
        # Error jika model belum siap
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        # Error umum lainnya
        print(f"Error detail: {e}")
        raise HTTPException(status_code=500, detail="Gagal memproses gambar pada server.")

    if detected_label is None:
        raise HTTPException(status_code=400, detail="Objek tidak dapat dikenali.")

    # 3. Ambil Detail dari Database
    object_info = OBJECT_DATABASE.get(detected_label, {
        "about": f"Objek terdeteksi sebagai {detected_label}, namun deskripsi detail belum tersedia.",
        "donts": ["Harap menjaga kesopanan dan menghormati budaya setempat"]
    })

    # 4. Kembalikan Hasil
    return {
        "model_used": model_type.value, # Memberi tahu user model apa yang akhirnya dipakai
        "object_name": detected_label,
        "accuracy": float(confidence),
        "about": object_info["about"],
        "donts": object_info["donts"]
    }