import os
import config
from core import OrquestadorInforme

def verificar_archivo(ruta, tipo):
    """Auxiliar para asegurar la existencia de los archivos locales de prueba."""
    if not os.path.exists(ruta):
        print(f"⚠️  [Aviso] No se encontró el archivo de {tipo}: '{ruta}'")
        return False
    return True

def main():
    print("==========================================================")
    print("🤖 INICIANDO PIPELINE MULTI-AGENTE (FASE 4: DISEÑO EDITORIAL)")
    print("==========================================================\n")

    # 1. Configuración del nivel de incidencia técnica (Parámetro clave de la Fase 3)
    NIVEL_INCIDENCIA = 0.85  

    # 1b. Configuración del enfoque psicológico (NUEVO - Parámetro clave Fase 4)
    # Opciones: 
    # - "comercial_preventivo" (Tono empático, didáctico, destaca valor comercial)
    # - "judicial_urgente" (Tono severo, normativo, destaca riesgos legales/físicos)
    ENFOQUE_PSICOLOGICO = "comercial_preventivo"  # Cambia según la intención de comunicación

    # 2. Inicializar el orquestador con su selector dinámico de agentes
    sistema = OrquestadorInforme()

    # 3. Definición de rutas para archivos de terreno de prueba
    foto_1 = "hallazgo1.jpeg"
    audio_1 = "audio_hallazgo1.ogg"

    foto_2 = "hallazgo2.jpeg"
    audio_2 = "audio_hallazgo2.ogg"

    audio_general = "audio_general.ogg"

    # 4. Verificación de archivos antes de iniciar llamadas de API
    archivos_ok = True
    archivos_ok &= verificar_archivo(foto_1, "imagen (Hallazgo 1)")
    archivos_ok &= verificar_archivo(audio_1, "audio (Hallazgo 1)")
    archivos_ok &= verificar_archivo(foto_2, "imagen (Hallazgo 2)")
    archivos_ok &= verificar_archivo(audio_2, "audio (Hallazgo 2)")
    archivos_ok &= verificar_archivo(audio_general, "audio (General)")

    if not archivos_ok:
        print("\n❌ [Error] Por favor, coloca los archivos multimedia requeridos en la raíz para probar el flujo.")
        return

    # 5. Registro de datos de terreno (Módulo de Percepción - Groq Vision/Whisper)
    print("\n--- [PASO 1] PERCEPCIÓN DE HALLAZGOS EN TERRENO ---")
    sistema.registrar_hallazgo(ruta_foto=foto_1, ruta_audio=audio_1)
    sistema.registrar_hallazgo(ruta_foto=foto_2, ruta_audio=audio_2)
    sistema.registrar_nota_general(ruta_audio_general=audio_general)

    # 6. Orquestación Multi-Agente y Redacción del LaTeX
    print(f"\n--- [PASO 2] CO-PENSAMIENTO MULTI-AGENTE (INCIDENCIA: {NIVEL_INCIDENCIA} | ENFOQUE: {ENFOQUE_PSICOLOGICO.upper()}) ---")
    codigo_latex = sistema.construir_informe(
        formato_clave="inspeccion",
        obra="Edificio Sol de Valparaíso - Bloque Alpha",
        inspector="Ing. Carlos Mendoza",
        tipo_doc="INFORME TÉCNICO DE TERRENO",
        incidencia=NIVEL_INCIDENCIA,
        enfoque=ENFOQUE_PSICOLOGICO # <-- PASAMOS EL NUEVO PARÁMETRO AL ORQUESTADOR
    )

    # 7. Escritura del archivo de salida
    nombre_archivo = f"informe_diseno_{ENFOQUE_PSICOLOGICO}.tex"
    ruta_salida = os.path.join(config.OUTPUT_DIR, nombre_archivo)
    
    # Crear directorio de salida si no existe
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(codigo_latex)

    print("\n==========================================================")
    print(f"🎉 ¡PIPELINE DE AGENTES COMPLETADO CON ÉXITO!")
    print(f"📂 Archivo LaTeX enriquecido generado en: {ruta_salida}")
    print("==========================================================")

if __name__ == "__main__":
    main()