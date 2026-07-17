# agents/expert.py
import os
from typing import List, Literal
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
import config

# =====================================================================
# 1. ESQUEMAS DE SALIDA ESTRUCTURADA (Pydantic v2)
# =====================================================================

class DecisionClasificador(BaseModel):
    """Esquema estricto que el Meta-Agente DEBE retornar."""
    especialidad: str = Field(
        description="Título de la especialidad de ingeniería requerida (ej. Ingeniero Civil Estructural, Ingeniero Geotécnico, Especialista Hidráulico)."
    )
    justificacion: str = Field(
        description="Breve explicación técnica de por qué se requiere esta especialidad basándose en los hallazgos."
    )
    system_prompt_experto: str = Field(
        description="System prompt detallado y riguroso diseñado a la medida para guiar al segundo agente especialista."
    )


class AnalisisExperto(BaseModel):
    """Análisis e insights de ingeniería que el Agente Experto proveerá a DeepSeek."""
    conceptos_clave: List[str] = Field(
        description="Lista de términos técnicos, normativas o patologías específicas aplicables al caso."
    )
    diagnostico_causa_raiz: str = Field(
        description="Explicación técnica de la posible causa origen del deterioro/situación."
    )
    soluciones_sugeridas: List[str] = Field(
        description="Lista de recomendaciones o métodos de reparación aplicables según estándares de ingeniería."
    )


# =====================================================================
# 2. IMPLEMENTACIÓN DE LOS AGENTES
# =====================================================================

class AgenteClasificador:
    """Meta-Agente (Triage) encargado de analizar el contexto y configurar al experto óptimo."""
    def __init__(self):
        # Usamos Instructor para parchear el cliente de OpenAI/Groq y forzar JSON estructurado
        self.client = instructor.from_openai(
            OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=config.GROQ_API_KEY
            )
        )

    def determinar_especialista(self, contexto_general: str, datos_hallazgos: str) -> DecisionClasificador:
        prompt_sistema = """
Eres el Ingeniero Jefe de una prestigiosa firma de consultoría. Tu rol es analizar los hallazgos preliminares de terreno 
y las notas generales para:
1. Determinar exactamente qué especialista técnico de ingeniería (civil, estructural, hidráulico, geotecnia, eléctrico, etc.) es el idóneo para analizar el caso.
2. Redactar un 'System Prompt' ultra-especializado para que ese experto evalúe los datos con el máximo rigor posible.
"""

        prompt_usuario = f"""
--- NOTAS GENERALES DE TERRENO ---
{contexto_general}

--- DETALLES DE LOS HALLAZGOS ---
{datos_hallazgos}
"""

        # Instructor garantiza que la salida sea un objeto Pydantic de tipo 'DecisionClasificador'
        decision: DecisionClasificador = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Excelente modelo de razonamiento rápido en Groq
            response_model=DecisionClasificador,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.1  # Baja temperatura para decisiones lógicas y deterministas
        )
        return decision


class AgenteExpertoTecnico:
    """Agente especialista que asesora técnicamente el proceso antes de la redacción del LaTeX."""
    def __init__(self):
        self.client = instructor.from_openai(
            OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=config.GROQ_API_KEY
            )
        )

    def asesorar_hallazgos(self, system_prompt_rol: str, datos_hallazgos: str, incidencia: float = 0.5) -> AnalisisExperto:
        """
        Analiza los hallazgos usando el rol inyectado y calibra su profundidad técnica mediante la variable 'incidencia'.
        incidencia (float): De 0.0 (análisis superficial, puramente descriptivo) a 1.0 (análisis denso de alta ingeniería).
        """
        
        # Ajustamos dinámicamente las directrices del prompt según el nivel de incidencia (influencia)
        directriz_incidencia = ""
        if incidencia < 0.3:
            directriz_incidencia = "Mantén un análisis conceptual simple y directo. Evita saturar con fórmulas o normativas complejas."
        elif incidencia < 0.7:
            directriz_incidencia = "Provee un análisis equilibrado. Usa terminología de ingeniería estándar y menciona prácticas comunes de reparación."
        else:
            directriz_incidencia = "Actúa con el máximo rigor académico y profesional. Propón diagnósticos patológicos avanzados, cita normativas internacionales aplicables e incluye especificaciones de ingeniería profunda."

        prompt_usuario = f"""
{directriz_incidencia}

Analiza los siguientes hallazgos de terreno y extrae un diagnóstico robusto:
{datos_hallazgos}
"""

        analisis: AnalisisExperto = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=AnalisisExperto,
            messages=[
                {"role": "system", "content": system_prompt_rol},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.2
        )
        return analisis