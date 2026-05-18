from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Cargar variables del .env
load_dotenv()

# Crear app FastAPI
app = FastAPI()

# Cliente OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Modelo de entrada
class SymptomsRequest(BaseModel):
    edad: int
    sexo: str
    sintomas: List[str]

# Ruta base
@app.get("/")
def home():
    return {
        "message": "MarIA backend funcionando correctamente"
    }

# Ruta principal de análisis
@app.post("/analyze")
def analyze(data: SymptomsRequest):

    prompt = f"""
Eres MarIA, una IA médica preventiva y asistente de apoyo clínico para profesionales de la salud.

Tu función es ayudar en el análisis preliminar de síntomas, identificar posibles condiciones médicas y generar recomendaciones preventivas.

NO debes dar diagnósticos definitivos.

Edad: {data.edad}
Sexo: {data.sexo}
Síntomas: {", ".join(data.sintomas)}

Responde ÚNICAMENTE en JSON válido con esta estructura:

{{
  "riesgo": "bajo/moderado/alto",
  "nivel_urgencia": "baja/media/alta",
  "posibles_condiciones": [
    {{
      "nombre": "nombre enfermedad",
      "probabilidad": 0
    }}
  ],
  "sintomas_clave": [
    "síntoma importante"
  ],
  "recomendaciones": [
    "recomendación 1"
  ],
  "alertas": [
    "alerta importante"
  ],
  "explicacion": "explicación médica breve orientada a apoyo clínico"
}}

Reglas:
- SOLO JSON
- SIN markdown
- SIN texto extra
"""

    # Llamada a OpenRouter (DeepSeek)
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response = completion.choices[0].message.content

    print("RESPUESTA IA:", response)

    if not response:
        return {
            "error": "IA no devolvió respuesta"
        }

    try:
        parsed_response = json.loads(response)
        return parsed_response

    except Exception:
        print("ERROR PARSEANDO:", response)
        return {
            "error": "Respuesta inválida de la IA",
            "raw": response
        }