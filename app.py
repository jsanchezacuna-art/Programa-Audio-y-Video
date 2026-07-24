import streamlit as st
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    page_title="Programa de Audio, Video y Salas",
    layout="wide"
)

st.title("📋 Generador de Programa de Audio, Video y Salas")

# --- 1. BARRA LATERAL (CONFIGURACIÓN DE HERMANOS Y PERÍODO) ---
with st.sidebar:
    st.header("⚙️ Configuración General")
    congregacion = st.text_input("Nombre de la Congregación", "El Gallito")
    periodo = st.text_input("Meses / Período", "Agosto y Septiembre 2026")
    
    st.markdown("---")
    st.subheader("👥 Lista Maestra de Hermanos")
    st.caption("Ingresa a todos los hermanos disponibles en la congregación (uno por línea):")
    
    hermanos_defecto = [
        "José Pereira", "José Alberto González", "David Herrera", "Rodney Alfaro",
        "Carlos Josué Pereira", "Julio Sánchez", "Iván Zamora", "Josué López",
        "Javier García", "Dashler Sánchez", "Kenneth Solís", "Walter Sánchez",
        "Sebastián Montero", "Carlos Blanco", "Elixander Alvarado",
        "Geremy Fernández", "Rafael Segura", "Roger Loaiza", "Carlos Enrique Pereira"
    ]
    
    hermanos_texto = st.text_area("Hermanos registrados:", value="\n".join(hermanos_defecto), height=280)
    lista_hermanos = [h.strip() for h in hermanos_texto.split("\n") if h.strip()]

# --- 2. ESTADO INICIAL DE LAS REUNIONES ---
if "reuniones" not in st.session_state:
    st.session_state.reuniones = [
        {"fecha": "02/08/2026", "dia": "Domingo", "sin_reunion": False, "responsables": [], "audio": "José Pereira", "video": "José Alberto González", "mic": "David Herrera", "acomodador": "Rodney Alfaro"},
        {"fecha": "05/08/2026", "dia": "Miércoles", "sin_reunion": False, "responsables": [], "audio": "Carlos Josué Pereira", "video": "Julio Sánchez", "mic": "Iván Zamora", "acomodador": "Josué López"},
        {"fecha": "09/08/2026", "dia": "Domingo", "sin_reunion": False, "responsables": [], "audio": "Javier García", "video": "Dashler Sánchez", "mic": "Kenneth Solís", "acomodador": "Walter Sánchez"},
        {"fecha": "12/08/2026", "dia": "Miércoles", "sin_reunion": True, "responsables": [], "audio": "", "video": "", "mic": "", "acomodador": ""},
        {"fecha": "16/08/2026", "dia": "Domingo", "sin_reunion": True, "responsables": [], "audio": "", "video": "", "mic": "", "acomodador": ""},
        {"fecha": "18/08/2026", "dia": "Martes", "sin_reunion": False, "responsables": [], "audio": "Sebastián Montero", "video": "Josué López", "mic": "Carlos Blanco", "acomodador": "Elixander Alvarado"},
        {"fecha": "23/08/2026", "dia": "Domingo", "sin_reunion": False, "responsables": [], "audio": "Geremy Fernández", "video": "José Alberto González", "mic": "Rafael Segura", "acomodador": "Roger Loaiza"},
        {"fecha": "26/08/2026", "dia": "Miércoles", "sin_reunion": False, "responsables": [], "audio": "David Herrera", "video": "Sebastián Montero", "mic": "Rafael Segura", "acomodador": "Carlos Enrique Pereira"},
        {"fecha": "30/08/2026", "dia": "Domingo", "sin_reunion": False, "responsables": [], "audio": "Dashler Sánchez", "video": "Carlos Josué Pereira", "mic": "Walter Sánchez", "acomodador": "Elixander Alvarado"},
    ]

st.subheader("🗓️ Programación de Fechas y Filtro de Disponibilidad")

col_btn1, col_btn2 = st.columns([2, 8])
with col_btn1:
    if st.button("➕ Agregar Fecha"):
        st.session_state.reuniones.append({
            "fecha": "01/09/2026", "dia": "Domingo", "sin_reunion": False, "responsables": [],
            "audio": "", "video": "", "mic": "", "acomodador": ""
        })
        st.rerun()

datos_programa_final = []

# --- 3. SECCIÓN DEDICADA PARA CADA FECHA ---
for idx, reun in enumerate(st.session_state.reuniones):
    with st.expander(f"📅 Reunión #{idx+1} — {reun['fecha']} ({reun['dia']})", expanded=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1])
        with col_f1:
            reun['fecha'] = st.text_input("Fecha", value=reun['fecha'], key=f"fecha_{idx}")
        with col_f2:
            dias_opciones = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
            idx_dia = dias_opciones.index(reun['dia']) if reun['dia'] in dias_opciones else 0
            reun['dia'] = st.selectbox("Día", dias_opciones, index=idx_dia, key=f"dia_{idx}")
        with col_f3:
            reun['sin_reunion'] = st.checkbox("🚫 NO HAY REUNIÓN", value=reun['sin_reunion'], key=f"sin_reunion_{idx}")
        with col_f4:
            st.write("")
            st.write("")
            if st.button("🗑️", key=f"del_{idx}", help="Eliminar esta fecha"):
                st.session_state.reuniones.pop(idx)
                st.rerun()

        if reun['sin_reunion']:
            st.info("Marcado como 'NO HAY REUNIÓN'.")
            datos_programa_final.append({
                "Fecha": reun['fecha'],
                "Día": reun['dia'],
                "Audio": "--- NO HAY REUNIÓN ---",
                "Video": "--- NO HAY REUNIÓN ---",
                "Micrófono": "--- NO HAY REUNIÓN ---",
                "Acomodador": "--- NO HAY REUNIÓN ---"
            })
        else:
            st.markdown("---")
            # PASO 1: RESPONSABILIDADES
            st.markdown("**1️⃣ Selecciona hermanos con asignación principal (Ocupados ese día):**")
            resp_validos = [h for h in reun['responsables'] if h in lista_hermanos]
            reun['responsables'] = st.multiselect(
                "Presidencia, Plataforma, Oradores, Lectores, etc.:",
                options=lista_hermanos,
                default=resp_validos,
                key=f"resp_{idx}",
                help="Los hermanos seleccionados aquí NO aparecerán en la lista para Audio, Video, Micrófono o Acomodador."
            )
            
            # FILTRAR DISPONIBLES
            disponibles = [h for h in lista_hermanos if h not in reun['responsables']]
            options_with_empty = ["-- Sin asignar --"] + disponibles

            # PASO 2: AUDIO Y VIDEO CON HERMANOS FILTRADOS
            st.markdown("**2️⃣ Asigna Audio, Video y Salas (Solo hermanos disponibles):**")
            st.caption(f"🟢 Quedan **{len(disponibles)}** hermanos disponibles para esta reunión.")

            col_a1, col_a2, col_a3, col_a4 = st.columns(4)

            def get_index(val, options):
                return options.index(val) if val in options else 0

            with col_a1:
                reun['audio'] = st.selectbox("Audio", options_with_empty, index=get_index(reun['audio'], options_with_empty), key=f"audio_{idx}")
            with col_a2:
                reun['video'] = st.selectbox("Video", options_with_empty, index=get_index(reun['video'], options_with_empty), key=f"video_{idx}")
            with col_a3:
                reun['mic'] = st.selectbox("Micrófono", options_with_empty, index=get_index(reun['mic'], options_with_empty), key=f"mic_{idx}")
            with col_a4:
                reun['acomodador'] = st.selectbox("Acomodador", options_with_empty, index=get_index(reun['acomodador'], options_with_empty), key=f"aco_{idx}")

            datos_programa_final.append({
                "Fecha": reun['fecha'],
                "Día": reun['dia'],
                "Audio": reun['audio'] if reun['audio'] != "-- Sin asignar --" else "",
                "Video": reun['video'] if reun['video'] != "-- Sin asignar --" else "",
                "Micrófono": reun['mic'] if reun['mic'] != "-- Sin asignar --" else "",
                "Acomodador": reun['acomodador'] if reun['acomodador'] != "-- Sin asignar --" else ""
            })

# --- 4. RENDERIZADO DEL PROGRAMA FINAL EN VISTA PREVIA Y DESCARGAS ---
filas_html = ""
for item in datos_programa_final:
    is_no_reunion = (item['Audio'] == "--- NO HAY REUNIÓN ---")
    clase_td = ' class="no-hay-reunion"' if is_no_reunion else ''
    
    filas_html += f"""
    <tr>
        <td>{item['Fecha']}</td>
        <td>{item['Día']}</td>
        <td{clase_td}>{item['Audio']}</td>
        <td{clase_td}>{item['Video']}</td>
        <td{clase_td}>{item['Micrófono']}</td>
        <td{clase_td}>{item['Acomodador']}</td>
    </tr>
    """

html_code = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
  <style>
    body {{
      font-family: Arial, Helvetica, sans-serif;
      background-color: #f4f6f9;
      margin: 0;
      padding: 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .panel-descargas {{
      margin-bottom: 20px;
      display: flex;
      gap: 15px;
      flex-wrap: wrap;
      justify-content: center;
    }}
    .btn-descarga {{
      padding: 10px 18px;
      font-size: 14px;
      font-weight: bold;
      color: #ffffff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }}
    .btn-imagen {{ background-color: #2b5876; }}
    .btn-pdf {{ background-color: #d9534f; }}
    .btn-excel {{ background-color: #1e7e34; }}
    #contenedor-programa {{
      width: 100%;
      max-width: 1000px;
      background-color: #ffffff;
      border: 1px solid #d0d7de;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      padding: 0 0 20px 0;
    }}
    .header-banner {{
      background-color: #224b7a;
      color: #ffffff;
      text-align: center;
      padding: 25px 15px;
    }}
    .header-banner h1 {{
      margin: 0 0 8px 0;
      font-size: 20px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .header-banner p {{ margin: 0; font-size: 14px; opacity: 0.9; }}
    .tabla-contenedor {{ padding: 15px; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; color: #333333; }}
    th {{ background-color: #34495e; color: #ffffff; padding: 10px 6px; text-align: center; border: 1px solid #34495e; }}
    td {{ padding: 9px 6px; text-align: center; border: 1px solid #e1e8ed; }}
    tr:nth-child(even) {{ background-color: #f8fafc; }}
    .no-hay-reunion {{ font-weight: bold; color: #555555; letter-spacing: 1px; }}
  </style>
</head>
<body>
  <div class="panel-descargas">
    <button class="btn-descarga btn-imagen" onclick="descargarImagen()">📷 Descargar Imagen (PNG)</button>
    <button class="btn-descarga btn-pdf" onclick="descargarPDF()">📄 Descargar PDF</button>
    <button class="btn-descarga btn-excel" onclick="descargarExcel()">📊 Descargar Excel</button>
  </div>

  <div id="contenedor-programa">
    <div class="header-banner">
      <h1>Programa de Audio, Video y Salas</h1>
      <p>Congregación {congregacion} | {periodo}</p>
    </div>
    <div class="tabla-contenedor">
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Día</th>
            <th>Audio</th>
            <th>Video</th>
            <th>Micrófono</th>
            <th>Acomodador</th>
          </tr>
        </thead>
        <tbody>
          {filas_html}
        </tbody>
      </table>
    </div>
  </div>

  <script>
    async function descargarImagen() {{
      await document.fonts.ready;
      const elemento = document.getElementById('contenedor-programa');
      html2canvas(elemento, {{ scale: 2, useCORS: true, backgroundColor: '#ffffff' }}).then(canvas => {{
        const enlace = document.createElement('a');
        enlace.download = 'Programa_Audio_Video_Salas.png';
        enlace.href = canvas.toDataURL('image/png');
        enlace.click();
      }});
    }}

    function descargarPDF() {{
      const elemento = document.getElementById('contenedor-programa');
      const opciones = {{
        margin: 0.3,
        filename: 'Programa_Audio_Video_Salas.pdf',
        image: {{ type: 'jpeg', quality: 0.98 }},
        html2canvas: {{ scale: 2, useCORS: true }},
        jsPDF: {{ unit: 'in', format: 'letter', orientation: 'landscape' }}
      }};
      html2pdf().set(opciones).from(elemento).save();
    }}

    function descargarExcel() {{
      const tabla = document.querySelector('#contenedor-programa table');
      if (!tabla) return;
      const libro = XLSX.utils.table_to_book(tabla, {{ sheet: "Programa" }});
      XLSX.writeFile(libro, 'Programa_Audio_Video_Salas.xlsx');
    }}
  </script>
</body>
</html>
"""

st.markdown("---")
st.subheader("👁️ Vista Previa Final")
components.html(html_code, height=750, scrolling=True)
