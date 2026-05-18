from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = FastAPI()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

class SymptomsRequest(BaseModel):
    edad: int
    sexo: str
    sintomas: List[str]

@app.get("/")
def home():
    return {
        "message": "MarIA backend funcionando correctamente"
    }

@app.post("/analyze")
def analyze(data: SymptomsRequest):

    prompt = f"""
Eres MarIA, una IA médica preventiva y asistente de apoyo clínico.

Tu función es analizar síntomas y ayudar como apoyo a profesionales de la salud.

NO des diagnósticos definitivos.

Edad: {data.edad}
Sexo: {data.sexo}
Síntomas: {", ".join(data.sintomas)}

Responde SOLO en JSON válido, sin markdown, sin ``` ni texto extra.

Formato requerido:
{{
  "riesgo": "bajo/moderado/alto",
  "nivel_urgencia": "baja/media/alta",
  "posibles_condiciones": [
    {{
      "nombre": "enfermedad",
      "probabilidad": 0
    }}
  ],
  "sintomas_clave": [],
  "recomendaciones": [],
  "alertas": [],
  "explicacion": ""
}}
"""

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response = completion.choices[0].message.content

        print("RESPUESTA IA:", response)

        if not response:
            raise ValueError("IA sin respuesta")

        # 🔥 LIMPIEZA DE RESPUESTA (ANTI ```json)
        clean = response.strip()

        if clean.startswith("```"):
            clean = clean.replace("```json", "")
            clean = clean.replace("```", "")
            clean = clean.strip()

        parsed = json.loads(clean)

        return parsed

    except Exception as e:

        print("ERROR EN ANALISIS:", str(e))

        # 🔥 RESPUESTA DE EMERGENCIA (NUNCA FALLA)
        return {
            "riesgo": "moderado",
            "nivel_urgencia": "media",
            "posibles_condiciones": [
                {
                    "nombre": "No se pudo determinar con precisión",
                    "probabilidad": 50
                }
            ],
            "sintomas_clave": data.sintomas,
            "recomendaciones": [
                "Consultar con un profesional de salud",
                "Mantener observación de síntomas"
            ],
            "alertas": [
                "Sistema de análisis temporalmente limitado"
            ],
            "explicacion": "No se pudo procesar completamente la respuesta de la IA, pero se genera una evaluación preventiva básica."
        }