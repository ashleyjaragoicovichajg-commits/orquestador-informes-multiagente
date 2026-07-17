import os
from openai import OpenAI

import config
from services.ai_perception import AIPerceptionService
from templates import PlantillaInspeccionVisual

# Importamos los agentes de la Fase 3 (Expertos)
from agents.expert import AgenteClasificador, AgenteExpertoTecnico

# 1. IMPORTAMOS LOS NUEVOS AGENTES DE COPYWRITING Y MAQUETACIÓN
from agents.copywriter import AgentePsicologoAudiencia, AgenteMaquetadorLatex


class OrquestadorInforme:
    def __init__(self):
        self.percepcion = AIPerceptionService()
        
        # Clientes de API
        self.client_deepseek = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        
        # Instanciamos todos los agentes
        self.clasificador = AgenteClasificador()
        self.experto = AgenteExpertoTecnico()
        
        # 2. INSTANCIAMOS LOS NUEVOS AGENTES
        self.psicologo = AgentePsicologoAudiencia()
        self.maquetador = AgenteMaquetadorLatex()
        
        # Almacenamiento temporal de datos del flujo
        self.hallazgos = []
        self.notes_generales = []  # Corregido typo si aplica, mantengo consistencia
        self.notas_generales = []
        
        # Mapeo de formatos disponibles
        self.formatos = {
            "inspeccion": PlantillaInspeccionVisual()
        }

    def registrar_hallazgo(self, ruta_foto, ruta_audio=None):
        print(f"[Percepción] Analizando hallazgo fotográfico: {ruta_foto}")
        txt_vision = self.percepcion.analizar_imagen(ruta_foto)
        
        txt_audio = ""
        if ruta_audio and os.path.exists(ruta_audio):
            print(f"[Percepción] Transcribiendo audio del hallazgo: {ruta_audio}")
            txt_audio = self.percepcion.transcribir_audio(ruta_audio)
        
        self.hallazgos.append({
            "id": len(self.hallazgos) + 1,
            "foto": ruta_foto,
            "txt_vision": txt_vision,
            "txt_audio": txt_audio
        })

    def registrar_nota_general(self, ruta_audio_general):
        if ruta_audio_general and os.path.exists(ruta_audio_general):
            print(f"[Percepción] Transcribiendo hilo conductor general: {ruta_audio_general}")
            txt_general = self.percepcion.transcribir_audio(ruta_audio_general)
            self.notas_generales.append(txt_general)

    # 3. AÑADIMOS EL PARÁMETRO "enfoque" AL MÉTODO
    def construir_informe(self, formato_clave, obra, inspector, tipo_doc, incidencia=0.5, enfoque="comercial_preventivo"):
        """
        Construye el informe final LaTeX utilizando la tubería completa de agentes:
        Clasificador -> Experto Técnico -> Psicólogo de Audiencia -> Maquetador LaTeX.
        """
        if formato_clave not in self.formatos:
            raise ValueError(f"Formato inválido. Elige uno de: {list(self.formatos.keys())}")
            
        plantilla = self.formatos[formato_clave]
        
        # Consolidamos los datos crudos recolectados de terreno
        prompt_datos_crudos = ""
        for h in self.hallazgos:
            prompt_datos_crudos += (
                f"\n### ELEMENTO #{h['id']}\n"
                f"- Archivo imagen: {h['foto']}\n"
                f"- Análisis Visual IA: {h['txt_vision']}\n"
                f"- Comentario de voz transcribido: {h['txt_audio']}\n"
            )
            
        prompt_contexto_general = "\n".join([f"- {n}" for n in self.notas_generales])
        
        # =====================================================================
        # 🧠 FASE A: AGENTES DE EXPERTICIA TÉCNICA
        # =====================================================================
        print("\n[Agente 1] Analizando terreno para determinar especialidad óptima...")
        decision_meta = self.clasificador.determinar_especialista(
            contexto_general=prompt_contexto_general,
            datos_hallazgos=prompt_datos_crudos
        )
        
        print(f"🎯 Especialista seleccionado: {decision_meta.especialidad}")
        
        print(f"\n[Agente 2] Solicitando asesoramiento al {decision_meta.especialidad}...")
        asesoria = self.experto.asesorar_hallazgos(
            system_prompt_rol=decision_meta.system_prompt_experto,
            datos_hallazgos=prompt_datos_crudos,
            incidencia=incidencia
        )
        
        # Combinamos datos crudos y criterio experto en un único reporte técnico consolidado
        reporte_tecnico_consolidado = f"""
PROYECTO: {obra}
INSPECTOR: {inspector}
TIPO DE DOCUMENTO: {tipo_doc}

--- CONTEXTO GENERAL ---
{prompt_contexto_general}

--- DATOS DE TERRENO ---
{prompt_datos_crudos}

--- INFORME DE ASESORÍA DE EXPERTO TÉCNICO ({decision_meta.especialidad}) ---
Conceptos clave y normativas:
{chr(10).join([f" - {c}" for c in asesoria.conceptos_clave])}

Diagnóstico causa raíz:
{asesoria.diagnostico_causa_raiz}

Soluciones sugeridas:
{chr(10).join([f" - {s}" for s in asesoria.soluciones_sugeridas])}
"""

        # =====================================================================
        # 🎭 FASE B: REFINAMIENTO PSICOLÓGICO Y EDITORIAL
        # =====================================================================
        print(f"\n[Agente 3 - Psicólogo] Adaptando tono técnico a perfil: '{enfoque.upper()}'...")
        # Genera el PlanPsicoVisual estructurado en base al reporte técnico técnico consolidado
        plan_visual = self.psicologo.refinar_informe(
            reporte_tecnico_crudo=reporte_tecnico_consolidado,
            enfoque=enfoque
        )

        # =====================================================================
        # 🎨 FASE C: MAQUETACIÓN EDITORIAL EN LATEX
        # =====================================================================
        print("\n[Agente 4 - Maquetador] Generando código LaTeX final optimizado...")
        # Obtenemos el template base como string para guiar al maquetador
        estructura_plantilla_str = plantilla.obtener_system_prompt() 
        
        # Generamos el cuerpo del documento final en LaTeX
        cuerpo_latex = self.maquetador.generar_codigo_latex(
            plan_visual=plan_visual,
            estructura_plantilla=estructura_plantilla_str
        )
            
        # Retornamos el documento completo inyectando el cuerpo generado en la estructura
        return plantilla.construir_documento(obra, inspector, tipo_doc, cuerpo_latex)