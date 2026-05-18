from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Cargar variables del archivo .env
load_dotenv()

# Crear app FastAPI
app = FastAPI()

# Configurar cliente OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Modelo de datos
class SymptomsRequest(BaseModel):
    edad: int
    sexo: str
    sintomas: List[str]

# Ruta principal
@app.get("/")
def home():
    return {
        "message": "MarIA backend funcionando correctamente"
    }

# Ruta de análisis médico
@app.post("/analyze")
def analyze(data: SymptomsRequest):

    # Crear prompt médico

    
    prompt = f"""
Eres MarIA, una IA médica preventiva y asistente de apoyo clínico para profesionales de la salud.

Tu función es ayudar en el análisis preliminar de síntomas, identificar posibles condiciones médicas y generar recomendaciones preventivas de apoyo para facilitar la evaluación médica.

NO debes dar diagnósticos definitivos.

Analiza los siguientes síntomas:

Edad: {data.edad}
Sexo: {data.sexo}
Síntomas: {", ".join(data.sintomas)}

Responde ÚNICAMENTE en formato JSON válido.

Usa EXACTAMENTE esta estructura:

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

Reglas IMPORTANTES:
- NO agregues texto fuera del JSON.
- NO uses markdown.
- NO pongas ```json.
- Las probabilidades deben estar entre 0 y 100.
- Las explicaciones deben ser clínicas, breves y profesionales.
- Las alertas deben enfocarse en posibles signos de gravedad o necesidad de atención médica.
"""

    # Llamada a DeepSeek
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Obtener respuesta
    response = completion.choices[0].message.content
    
    parsed_response = json.loads(response)
    
    return parsed_response