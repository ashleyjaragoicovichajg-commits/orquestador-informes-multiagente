# services/ai_perception.py
import base64
import os
from groq import Groq
import config

class AIPerceptionService:
    """Servicio encargado de interactuar con los modelos cognitivos de entrada (Ojos y Oídos)."""
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)

    def _encode_image(self, image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

    def transcribir_audio(self, audio_path):
        if not audio_path or not os.path.exists(audio_path):
            return ""
        with open(audio_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                file=audio_file,
                model=config.MODELO_AUDIO,
                language="es",
                response_format="json",
                temperature=0.0
            )
            return response.text

    def analizar_imagen(self, image_path):
        if not image_path or not os.path.exists(image_path):
            return "Sin datos visuales."
        
        img_b64 = self._encode_image(image_path)
        response = self.client.chat.completions.create(
            model=config.MODELO_VISION,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe con rigor técnico los componentes de ingeniería, deterioros o detalles físicos visibles."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ],
            temperature=0.1
        )
        return response.choices[0].message.content