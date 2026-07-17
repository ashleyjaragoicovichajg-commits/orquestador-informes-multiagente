# agents/copywriter.py
from typing import List, Dict, Literal
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
import config

# =====================================================================
# 1. ESQUEMAS DE ESTRUCTURA SEMÁNTICA (Pydantic v2)
# =====================================================================

class ElementoVisual(BaseModel):
    """Define qué parte del texto necesita un tratamiento visual especial en LaTeX."""
    tipo_destaque: Literal["alerta_critica", "nota_suave", "lista_chek", "destaque_negrita"] = Field(
        description="El estilo visual que debe aplicar el maquetador LaTeX según la psicología de la audiencia."
    )
    texto_afectado: str = Field(
        description="La frase, párrafo o recomendación exacta que debe envolverse en esta estructura visual."
    )
    justificacion_psicologica: str = Field(
        description="Por qué es necesario destacar este punto específico para influir en este tipo de lector."
    )

class SeccionRefinada(BaseModel):
    """Representa una sección del informe procesada psicológicamente."""
    titulo: str = Field(description="Título formal de la sección.")
    texto_redactado: str = Field(
        description="El cuerpo de texto reescrito adaptando el vocabulario, nivel de riesgo y tono al perfil de la audiencia."
    )
    elementos_visuales: List[ElementoVisual] = Field(
        default=[],
        description="Lista de fragmentos dentro de esta sección que requieren un diseño visual LaTeX especial."
    )

class PlanPsicoVisual(BaseModel):
    """La ficha técnica que el Psicólogo le entrega al Maquetador LaTeX."""
    enfoque_aplicado: str = Field(description="El perfil de enfoque seleccionado (ej. comercial, judicial, mitigador).")
    paleta_colores_latex: Dict[str, str] = Field(
        description="Definición de colores institucionales sugeridos para el PDF (ej. {'primary': 'DarkRed', 'secondary': 'DarkOrange'} o {'primary': 'NavyBlue', 'secondary': 'ForestGreen'})."
    )
    secciones: List[SeccionRefinada] = Field(
        description="Secciones del informe completamente pulidas en tono y con su mapa de destaques visuales listo."
    )


# =====================================================================
# 2. IMPLEMENTACIÓN DE LOS AGENTES
# =====================================================================

class AgentePsicologoAudiencia:
    """Agente encargado de reescribir el contenido técnico bajo un sesgo de influencia psicológica y comercial."""
    def __init__(self):
        self.client = instructor.from_openai(
            OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=config.GROQ_API_KEY
            )
        )

    def refinar_informe(self, reporte_tecnico_crudo: str, enfoque: Literal["judicial_urgente", "comercial_preventivo"]) -> PlanPsicoVisual:
        
        prompt_sistema = f"""
Eres un especialista en Psicología de la Comunicación y Redacción Técnica-Comercial enfocado en proyectos de ingeniería. 
Tu trabajo es recibir un reporte de ingeniería y transformarlo en un plan psico-visual de alto impacto.

Tu audiencia y enfoque para este caso es: **{enfoque.upper()}**

Directrices de tono según el enfoque:
1. JUDICIAL_URGENTE: Usa un tono asertivo, severo y formal. Enfatiza los riesgos latentes de no actuar de inmediato. Usa terminología de cumplimiento normativo. Sugiere colores de advertencia (rojos, naranjos oscuros) para el LaTeX.
2. COMERCIAL_PREVENTIVO: Usa un tono didáctico, empático y orientado a la solución. Evita generar pánico innecesario en el cliente, pero haz obvias las ventajas comerciales y de valor de propiedad de realizar reparaciones tempranas. Sugiere colores corporativos estables (azules, verdes secos) para el LaTeX.
"""

        prompt_usuario = f"""
Por favor, analiza el siguiente informe técnico y genera la ficha de diseño psico-visual estructurada:

--- INFORME TÉCNICO DE INGENIERÍA ---
{reporte_tecnico_crudo}
"""

        plan: PlanPsicoVisual = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=PlanPsicoVisual,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.3
        )
        return plan


class AgenteMaquetadorLatex:
    """Agente experto en diseño editorial LaTeX que materializa la intención psicológica en código compilable."""
    def __init__(self):
        # Usamos DeepSeek para la generación del código LaTeX final por su excelente precisión sintáctica
        self.client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )

    def generar_codigo_latex(self, plan_visual: PlanPsicoVisual, estructura_plantilla: str) -> str:
        
        prompt_sistema = f"""
Eres un tipógrafo y maquetador experto en LaTeX de nivel editorial científico. Tu único trabajo es recibir un Plan Psico-Visual estructurado en JSON y renderizarlo en código LaTeX impecable, limpio y libre de errores de compilación.

Debes aplicar visualmente las directrices del plan psicológico utilizando las macros de diseño que tengas disponibles en la plantilla:
- Si el plan indica un elemento 'alerta_critica', envuélvelo en una caja destacada (ej. tcolorbox con bordes gruesos y fondo de advertencia).
- Si indica 'nota_suave', usa cajas redondeadas de colores pasteles o sutiles.
- Si indica 'lista_chek', usa entornos itemize personalizados con iconos (ej. \\faCheck).
- Configura las variables de color del documento (PrimaryColor y SecondaryColor) utilizando la paleta provista en el plan.

Asegúrate de escapar correctamente caracteres especiales de LaTeX (como %, &, _, #) que vengan dentro de los textos redactados para evitar que el compilador se rompa.
"""

        # Convertimos el objeto Pydantic en una representación JSON legible para el LLM
        datos_json_plan = plan_visual.model_dump_json(indent=2)

        prompt_usuario = f"""
--- PLANTILLA LATEX BASE (GUÍA DE ESTILO) ---
{estructura_plantilla}

--- PLAN PSICO-VISUAL (CONTENIDO Y DIRECTRICES DE DISEÑO) ---
{datos_json_plan}

Genera únicamente el cuerpo de texto formateado en LaTeX. No incluyas explicaciones en prosa fuera del bloque de código.
"""

        response = self.client.chat.completions.create(
            model=config.MODELO_REDACCION,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.1  # Muy baja temperatura para evitar errores de sintaxis en el código LaTeX
        )
        
        cuerpo = response.choices[0].message.content.strip()
        if cuerpo.startswith("```"):
            cuerpo = cuerpo.replace("```latex", "").replace("```tex", "").replace("```", "")
        return cuerpo