# config.py
import os
from dotenv import load_dotenv

# Forzar la carga buscando el archivo en el directorio actual
ruta_env = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=ruta_env)

# --- LLAVES DE API ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "TU_LLAVE_GROQ_AQUI")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "TU_LLAVE_DEEPSEEK_AQUI")

# --- SELECCIÓN DE MODELOS ---
MODELO_VISION = "qwen/qwen3.6-27b"           # Ejecutado en Groq
MODELO_AUDIO = "whisper-large-v3-turbo"       # Ejecutado en Groq
MODELO_REDACCION = "deepseek-chat"            # DeepSeek-V3 / Coder

# --- CONFIGURACIONES DE SISTEMA ---
OUTPUT_DIR = "informes_generados"
os.makedirs(OUTPUT_DIR, exist_ok=True)