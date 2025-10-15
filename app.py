from fastapi import FastAPI, HTTPException
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

# Cargar el modelo y recursos
try:
    model = joblib.load('bot_detection_model.pkl')
    scaler = joblib.load('scaler.pkl') 
    feature_names = joblib.load('feature_names.pkl')
    print("✅ Modelo y recursos cargados exitosamente!")
    print(f"📊 Features cargados: {len(feature_names)}")
except Exception as e:
    print(f"❌ Error cargando el modelo: {e}")
    # En Render, si falla, al menos la app inicia
    model = scaler = feature_names = None

# Definir la estructura de entrada
class UserProfile(BaseModel):
    # Solo incluye las features más importantes para simplificar
    has_photo: float = 1.0
    is_verified: float = 0.0
    has_website: float = 0.0
    subscribers_count: float = 100.0
    city: float = 1.0
    can_send_message: float = 1.0
    is_profile_closed: float = 0.0
    has_status: float = 0.0
    is_blacklisted: float = 0.0
    # Agrega aquí el resto de tus 59 features...
    # Puedes copiar la lista completa que tenías antes

# Página de inicio
@app.get("/hello")
async def hello():
    return {
        "message": "¡Bienvenido al Bot Detection API!",
        "instrucciones": "Ve a la raíz (/) para usar la interfaz interactiva",
        "model_status": "Cargado" if model else "No cargado"
    }

# Endpoint de salud
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_loaded": model is not None,
        "total_features": len(feature_names) if feature_names else 0
    }

# Endpoint de predicción SIMPLIFICADO
@app.post("/predict")
async def predict_bot(profile: UserProfile):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")
    
    try:
        # Convertir el perfil a array (usando valores por defecto para features faltantes)
        input_dict = profile.dict()
        
        # Crear array con todas las features en el orden correcto
        input_array = []
        for feature in feature_names:
            if feature in input_dict:
                input_array.append(input_dict[feature])
            else:
                # Valor por defecto si la feature no está en el input
                input_array.append(0.0)
        
        input_data = np.array([input_array])
        
        # Escalar y predecir
        scaled_data = scaler.transform(input_data)
        prediction = model.predict(scaled_data)
        probability = model.predict_proba(scaled_data)
        
        # Interpretar resultados
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

# Endpoint de ejemplo con datos predefinidos
@app.get("/predict-example")
async def predict_example():
    """Ejemplo de predicción con datos de prueba"""
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
    
    # Llamar al endpoint de predicción
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.post("/predict", json=example_profile)
    
    return response.json()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)