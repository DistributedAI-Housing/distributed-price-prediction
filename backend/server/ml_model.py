import os
import joblib

def load_model():
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "price_model.pkl")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Le modèle n'a pas été trouvé : {MODEL_PATH}")
    return joblib.load(MODEL_PATH)
