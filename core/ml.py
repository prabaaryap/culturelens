# core/ml.py

import tensorflow as tf
import numpy as np
from PIL import Image
import io
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as preprocess_mobilenet
from tensorflow.keras.applications.efficientnet import preprocess_input as preprocess_efficientnet

# --- KONFIGURASI MODEL ---
# Pastikan file .h5 berada di root folder (sejajar dengan main.py)
PATH_MOBILENET = "MobileNetV2.h5"
PATH_EFFICIENTNET = "EfficienNet-B0.h5" # Sesuai nama file Anda (Typo 'Efficien' dijaga agar tidak error)

# Label harus sama persis urutannya dengan saat training
LABELS = [
    'Canang', 
    'Kwangen', 
    'Pelangkiran', 
    'Penjor', 
    'Sanggah Cucuk', 
    'banten', 
    'pelinggih'
]

# Variabel Global untuk menyimpan model di memori
loaded_models = {
    "mobilenet": None,
    "efficientnet": None
}

def load_models_at_startup():
    """
    Fungsi ini dipanggil saat server start.
    Tujuannya agar model sudah siap di RAM sebelum ada request masuk.
    """
    print("--- [ML CORE] Memulai Loading Model ---")
    
    # 1. Load MobileNetV2
    try:
        print(f"Loading {PATH_MOBILENET}...")
        loaded_models["mobilenet"] = tf.keras.models.load_model(PATH_MOBILENET)
        print("✅ MobileNetV2 Berhasil Dimuat.")
    except Exception as e:
        print(f"❌ Gagal memuat MobileNetV2: {e}")

    # 2. Load EfficientNet
    try:
        print(f"Loading {PATH_EFFICIENTNET}...")
        loaded_models["efficientnet"] = tf.keras.models.load_model(PATH_EFFICIENTNET)
        print("✅ EfficientNet Berhasil Dimuat.")
    except Exception as e:
        print(f"❌ Gagal memuat EfficientNet: {e}")

# Jalankan loading secara otomatis saat file ini di-import
load_models_at_startup()

def predict_object(image_bytes, model_type="mobilenet"):
    """
    Fungsi utama untuk melakukan prediksi.
    Menerima: bytes gambar dan tipe model ('mobilenet' atau 'efficientnet')
    Mengembalikan: (label, confidence_score)
    """
    # Ambil model dari memori
    model = loaded_models.get(model_type)
    
    if model is None:
        raise ValueError(f"Model '{model_type}' belum siap atau gagal dimuat di server.")

    try:
        # 1. Buka Gambar & Convert ke RGB
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # 2. Resize (Standar 224x224 untuk kedua model ini)
        image = image.resize((224, 224))
        
        # 3. Ubah ke Array Numpy & Tambah Dimensi Batch
        img_array = np.array(image)
        img_array = np.expand_dims(img_array, axis=0)
        
        # 4. Preprocessing (Kunci agar akurasi tinggi)
        # MobileNet dan EfficientNet butuh format input angka yang berbeda
        if model_type == "mobilenet":
            img_array = preprocess_mobilenet(img_array)
        elif model_type == "efficientnet":
            img_array = preprocess_efficientnet(img_array)

        # 5. Prediksi
        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        
        # 6. Ambil hasil terbaik
        class_index = np.argmax(score)
        confidence = 100 * np.max(score)
        detected_label = LABELS[class_index]
        
        return detected_label, confidence

    except Exception as e:
        print(f"Error pada ML Core: {e}")
        return None, 0.0