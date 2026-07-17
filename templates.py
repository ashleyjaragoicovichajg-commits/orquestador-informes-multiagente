# templates.py

class PlantillaInspeccionVisual:
    """Formato enfocado en patologías, fallas visuales y riesgos en terreno."""
    def obtener_system_prompt(self):
        return """Eres un Ingeniero Inspector experto en terreno. Tu trabajo es redactar los hallazgos de una inspección técnica visual en LaTeX.
Genera únicamente el cuerpo de las secciones (comenzando directamente en \\section{}). No incluyas preámbulo ni \\begin{document}.

Reglas:
1. Para cada hallazgo, crea una \\subsection{Hallazgo #X: <Título>}
2. Inserta la imagen asociada usando exactamente:
\\begin{figure}[H]
    \\centering
    \\includegraphics[width=0.65\\linewidth]{<RUTA_DE_LA_IMAGEN>}
    \\caption{Hallazgo #X: <Breve descripción técnica>}
    \\label{fig:hallazgo_X}
\\end{figure}
3. Destaca riesgos con: \\begin{quote}\\textbf{Riesgo / Impacto Detectado:} <Texto>\\end{quote}
4. Escapa caracteres: %, _, #, &, $."""

    def construir_documento(self, titulo_obra, inspector, tipo_doc, cuerpo_latex):
        return f"""\\documentclass[11pt, letterpaper]{{article}}
\\usepackage[spanish, es-tabla]{{babel}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[margin=2cm]{{geometry}}
\\usepackage{{graphicx, float, booktabs, hyperref, xcolor, fancyhdr, tcolorbox}}

\\definecolor{{navyblue}}{{HTML}}{{1B365D}}
\\definecolor{{slate}}{{HTML}}{{5C768D}}
\\hypersetup{{colorlinks=true, linkcolor=navyblue, urlcolor=slate}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{\\small \\color{{slate}}Reporte Técnico Visual}}
\\fancyhead[R]{{\\small \\color{{slate}}{titulo_obra}}}
\\fancyfoot[C]{{\\thepage}}

\\begin{{document}}
\\begin{{tcolorbox}}[colback=navyblue,colframe=navyblue,arc=0mm,top=10pt,bottom=10pt,left=15pt]
    \\color{{white}}\\Large\\bfseries {tipo_doc} \\\\ \\large\\mdseries {titulo_obra}
\\end{{tcolorbox}}

\\vspace{{0.2cm}}
\\begin{{tabular}}{{@{{}}ll}}
    \\textbf{{Inspector:}} & {inspector} \\\\
    \\textbf{{Fecha:}} & \\today
\\end{{tabular}}

\\vspace{{0.3cm}}\\noindent\\rule{{\\linewidth}}{{0.8pt}}\\vspace{{0.4cm}}
{cuerpo_latex}
\\end{{document}}"""

# Puedes añadir aquí las clases PlantillaTrabajosRealizados y PlantillaPresupuesto que definimos antes.