# core/ml.py

import tensorflow as tf

# Pastikan nama file ini SAMA PERSIS dengan file yang Anda copy
MODEL_PATH = "model_culturelens_mobilnetv2.h5" 

try:
    # Karena file ada di sebelah main.py, kita bisa load langsung
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    # ... error handling ...