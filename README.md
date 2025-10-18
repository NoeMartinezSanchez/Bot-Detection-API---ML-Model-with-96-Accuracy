# 🤖 Bot Detection API

![Python](https://img.shields.io/badge/Python-3.11-blue) 
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.2-green) 
![Render](https://img.shields.io/badge/Deployed%20on-Render-blueviolet)

Sistema inteligente para detectar perfiles bots en redes sociales usando **Machine Learning** y **FastAPI**.

---

## 📌 Descripción del Proyecto

La **Bot Detection API** permite analizar perfiles de usuario en redes sociales para determinar si son bots o humanos, con:

- Predicción probabilística de bots.
- Nivel de riesgo (BAJO, MEDIO, ALTO) basado en la probabilidad.
- Recomendaciones automáticas según el resultado.
- Integración fácil vía HTTP, formularios web o apps externas.

Está diseñada para ser **escalable, confiable y fácil de desplegar** en plataformas como **Render**.

---

## 🛠 Tecnologías Utilizadas

- **Python 3.11**
- **FastAPI** – Framework para APIs rápidas y modernas
- **scikit-learn** – Modelos de Machine Learning
- **pandas, numpy, joblib** – Manipulación de datos y serialización de modelos
- **Uvicorn** – Servidor ASGI para despliegue
- **HTML/CSS/JS** – Formulario web interactivo para pruebas

---

## 🚀 Despliegue

La API está desplegada en **Render**:

[https://bot-detection-api-ml-model-with-96-e1p3.onrender.com](https://bot-detection-api-ml-model-with-96-e1p3.onrender.com)

Endpoints disponibles:

| Método | Endpoint           | Descripción                                     |
|--------|------------------|-----------------------------------------------|
| GET    | `/hello`          | Mensaje de bienvenida                           |
| GET    | `/health`         | Estado de la API y modelo                       |
| POST   | `/predict`        | Predicción de un perfil de usuario             |
| GET    | `/predict-example`| Ejemplo de predicción con datos predefinidos   |

---

## ⚙️ Cómo Usar

### 1. Ejemplo de predicción con `curl`:

```bash
curl -X POST "https://bot-detection-api-ml-model-with-96-e1p3.onrender.com/predict" \
-H "Content-Type: application/json" \
-d '{
    "has_photo": 1,
    "is_verified": 0,
    "has_website": 0,
    "subscribers_count": 150,
    "city": 1,
    "can_send_message": 1,
    "is_profile_closed": 0,
    "has_status": 0,
    "is_blacklisted": 0
}'

