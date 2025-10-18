from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <-- Importar CORS
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from typing import List
import os

# Crear la aplicación FastAPI
app = FastAPI(
    title="🤖 Bot Detection API",
    description="Sistema inteligente para detectar perfiles bots en redes sociales",
    version="1.0.0",
    docs_url="/"  # La documentación estará en la raíz
)

# -------------------------------
# HABILITAR CORS PARA ACCESO DESDE HTML/OTROS DOMINIOS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- Permitir cualquier origen (puedes poner tu dominio específico)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar el modelo y recursos
try:
    model = joblib.load('bot_detection_model.pkl')
    scaler = joblib.load('scaler.pkl') 
    feature_names = joblib.load('feature_names.pkl')
    print("✅ Modelo y recursos cargados exitosamente!")
    print(f"📊 Features cargados: {len(feature_names)}")
except Exception as e:
    print(f"❌ Error cargando el modelo: {e}")
    model = scaler = feature_names = None

# Definir la estructura de entrada
class UserProfile(BaseModel):
    has_photo: float = 1.0
    is_verified: float = 0.0
    has_website: float = 0.0
    subscribers_count: float = 100.0
    city: float = 1.0
    can_send_message: float = 1.0
    is_profile_closed: float = 0.0
    has_status: float = 0.0
    is_blacklisted: float = 0.0
    # Agrega aquí el resto de tus features

# -------------------------------
# ENDPOINTS
# -------------------------------

@app.get("/hello")
async def hello():
    return {
        "message": "¡Bienvenido al Bot Detection API!",
        "instrucciones": "Ve a la raíz (/) para usar la interfaz interactiva",
        "model_status": "Cargado" if model else "No cargado"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "total_features": len(feature_names) if feature_names else 0
    }

@app.post("/predict")
async def predict_bot(profile: UserProfile):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")
    try:
        input_dict = profile.dict()
        input_array = [input_dict.get(f, 0.0) for f in feature_names]
        input_data = np.array([input_array])
        scaled_data = scaler.transform(input_data)
        prediction = model.predict(scaled_data)
        probability = model.predict_proba(scaled_data)
        bot_prob = probability[0][1] * 100
        human_prob = probability[0][0] * 100
        if prediction[0] == 1:
            result = "🤖 BOT DETECTADO"
            risk = "ALTO" if bot_prob > 80 else "MEDIO"
            recommendation = "Investigar perfil"
        else:
            result = "👤 HUMANO"
            risk = "BAJO"
            recommendation = "Perfil legítimo"
        return {
            "prediccion": result,
            "confianza": f"{max(bot_prob, human_prob):.1f}%",
            "probabilidad_bot": f"{bot_prob:.1f}%",
            "probabilidad_humano": f"{human_prob:.1f}%",
            "nivel_riesgo": risk,
            "recomendacion": recommendation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

@app.get("/predict-example")
async def predict_example():
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")
    example_profile = {
        "has_photo": 1.0,
        "is_verified": 0.0,
        "has_website": 0.0,
        "subscribers_count": 150.0,
        "city": 1.0,
        "can_send_message": 1.0,
        "is_profile_closed": 0.0,
        "has_status": 0.0,
        "is_blacklisted": 0.0
    }
    input_array = [example_profile.get(f, 0.0) for f in feature_names]
    input_data = np.array([input_array])
    scaled_data = scaler.transform(input_data)
    prediction = model.predict(scaled_data)
    probability = model.predict_proba(scaled_data)
    bot_prob = probability[0][1] * 100
    human_prob = probability[0][0] * 100
    if prediction[0] == 1:
        result = "🤖 BOT DETECTADO"
        risk = "ALTO" if bot_prob > 80 else "MEDIO"
        recommendation = "Investigar perfil"
    else:
        result = "👤 HUMANO"
        risk = "BAJO"
        recommendation = "Perfil legítimo"
    return {
        "prediccion": result,
        "confianza": f"{max(bot_prob, human_prob):.1f}%",
        "probabilidad_bot": f"{bot_prob:.1f}%",
        "probabilidad_humano": f"{human_prob:.1f}%",
        "nivel_riesgo": risk,
        "recomendacion": recommendation
    }

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

