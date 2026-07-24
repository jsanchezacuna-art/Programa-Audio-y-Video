import streamlit as st
import streamlit.components.v1 as components
import datetime
import calendar

# Configuración de la página
st.set_page_config(
    page_title="Programa de Audio, Video y Salas",
    layout="wide"
)

st.title("📋 Generador de Programa de Audio, Video y Salas")

# --- DICCIONARIOS Y DÍAS ---
MESES_LISTA = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

MESES_DICT = {nombre: i + 1 for i, nombre in enumerate(MESES_LISTA)}

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# --- FUNCIÓN PARA GENERAR FECHAS AUTOMÁTICAS ---
def generar_fechas_meses(anio, meses_seleccionados, dia_entre_semana="Miércoles"):
    dias_map = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}
    target_midweek = dias_map.get(dia_entre_semana, 2)
    
    reuniones_generadas = []
    
    for mes_nombre in meses_seleccionados:
        mes_num = MESES_DICT[mes_nombre]
        num_dias = calendar.monthrange(anio, mes_num)[1]
        
        for dia in range(1, num_dias + 1):
            dt = datetime.date(anio, mes_num, dia)
            # Entre semana habitual
            if dt.weekday() == target_midweek:
                reuniones_generadas.append({
                    "dt": dt,
                    "fecha": dt.strftime("%d/%m/%Y"),
                    "dia": dia_entre_semana,
                    "sin_reunion": False,
                    "responsables": [],
                    "audio": "-- Sin asignar --",
                    "video": "-- Sin asignar --",
                    "mic": "-- Sin asignar --",
                    "acomodador": "-- Sin asignar --"
                })
            # Fin de semana (Domingo)
            elif dt.weekday() == 6:
                reuniones_generadas.append({
                    "dt": dt,
                    "fecha": dt.strftime("%d/%m/%Y"),
                    "dia": "Domingo",
                    "sin_reunion": False,
                    "responsables": [],
                    "audio": "-- Sin asignar --",
                    "video": "-- Sin asignar --",
                    "mic": "-- Sin asignar --",
                    "acomodador": "-- Sin asignar --"
                })
                
    # Ordenar por fecha cronológica
    reuniones_generadas.sort(key=lambda x: x["dt"])
    return reuniones_generadas


# --- 1. BARRA LATERAL (CONFIGURACIÓN DE AÑO, MESES Y HERMANOS) ---
with st.sidebar:
    st.header("⚙️ Configuración del Período")
    congregacion = st.text_input("Nombre de la Congregación", "El Gallito")
    
    # SELECCIÓN DE AÑO Y CANTIDAD DE MESES
    anio_actual = datetime.datetime.now().year
    anio = st.number_input("Año", min_value=2024, max_value=2035, value=2026, step=1)
    
    cant_meses = st.radio("Cantidad de Meses a programar:", ["1 Mes", "2 Meses"], index=1)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        mes_1 = st.selectbox("Mes 1", MESES_LISTA, index=7) # Agosto por defecto
    
    meses_seleccionados = [mes_1]
    
    if cant_meses == "2 Meses":
        with col_m2:
            idx_m2 = (MESES_LISTA.index(mes_1) + 1) % 12
            mes_2 = st.selectbox("Mes 2", MESES_LISTA, index=idx_m2) # Septiembre por defecto
        meses_seleccionados.append(mes_2)
        periodo_str = f"{mes_1} y {mes_2} {anio}"
    else:
        periodo_str = f"{mes_1} {anio}"
        
    st.markdown(f"**Período activo:** `{periodo_str}`")
    
    dia_habitual_entre_semana = st.selectbox(
        "Día habitual entre semana:",
        ["Miércoles", "Martes", "Jueves", "Lunes"],
        index=0
    )
    
    st.markdown("---")
    if st.button("🔄 Cargar Fechas del Período"):
        st.session_state.reuniones = generar_fechas_meses(
            anio=anio,
            meses_seleccionados=meses_seleccionados,
            dia_entre_semana=dia_habitual_entre_semana
        )
        st.success("¡Fechas cargadas correctamente!")
        st.rerun()

    st.markdown("---")
    st.subheader("👥 Lista Maestra de Hermanos")
    hermanos_defecto = [
        "José Pereira", "José Alberto González", "David Herrera", "Rodney Alfaro",
        "Carlos Josué Pereira", "Julio Sánchez", "Iván Zamora", "Josué López",
        "Javier García", "Dashler Sánchez", "Kenneth Solís", "Walter Sánchez",
        "Sebastián Montero", "Carlos Blanco", "Elixander Alvarado",
        "Geremy Fernández", "Rafael Segura", "Roger Loaiza", "Carlos Enrique Pereira"
    ]
    
    hermanos_texto = st.text_area("Hermanos registrados (uno por línea):", value="\n".join(hermanos_defecto), height=240)
    lista_hermanos = [h.strip() for h in hermanos_texto.split("\n") if h.strip()]


# --- 2. INICIALIZACIÓN DE SESIÓN DE REUNIONES ---
if "reuniones" not in st.session_state or len(st.session_state.reuniones) == 0:
    st.session_state.reuniones = generar_fechas_meses(
        anio=anio,
        meses_seleccionados=meses_seleccionados,
        dia_entre_semana=dia_habitual_entre_semana
    )

st.subheader(f"🗓️ Programación de Fechas — {periodo_str}")

col_btn1, col_btn2 = st.columns([3, 7])
with col_btn1:
    if st.button("➕ Agregar Fecha Manual"):
        st.session_state.reuniones.append({
            "fecha": f"01/{MESES_DICT[mes_1]:02d}/{anio}",
            "dia": "Miércoles",
            "sin_reunion": False,
            "responsables": [],
            "audio": "-- Sin asignar --",
            "video": "-- Sin asignar --",
            "mic": "-- Sin asignar --",
            "acomodador": "-- Sin asignar --"
        })
        st.rerun()

datos_programa_final = []

# --- 3. EDITOR DE REUNIONES POR FECHA ---
for idx, reun in enumerate(st.session_state.reuniones):
    with st.expander(f"📅 #{idx+1} — {reun['fecha']} ({reun['dia']})", expanded=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 3, 1])
        
        with col_f1:
            reun['fecha'] = st.text_input("Fecha", value=reun['fecha'], key=f"fecha_{idx}")
            
        with col_f2:
            idx_dia = DIAS_SEMANA.index(reun['dia']) if reun['dia'] in DIAS_SEMANA else 2
            reun['dia'] = st.selectbox("Día de la reunión", DIAS_SEMANA, index=idx_dia, key=f"dia_{idx}", help="Puedes cambiar el día (por ejemplo, pasar de miércoles a martes).")
            
        with col_f3:
            reun['sin_reunion'] = st.checkbox("🚫 CANCELAR SEMANA / ASAMBLEA", value=reun['sin_reunion'], key=f"sin_reunion_{idx}")
            
        with col_f4:
            st.write("")
            st.write("")
            if st.button("🗑️", key=f"del_{idx}", help="Eliminar fecha"):
                st.session_state.reuniones.pop(idx)
                st.rerun()

        if reun['sin_reunion']:
            st.warning("⚠️ Reunión cancelada / Semana de Asamblea.")
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
            # PASO 1: RESPONSABILIDADES PRINCIPALES
            st.markdown("**1️⃣ Selecciona hermanos con asignación principal (Presidencia, Discursos, Plataforma, Lector, etc.):**")
            resp_validos = [h for h in reun.get('responsables', []) if h in lista_hermanos]
            reun['responsables'] = st.multiselect(
                "Hermanos ocupados este día:",
                options=lista_hermanos,
                default=resp_validos,
                key=f"resp_{idx}"
            )
            
            # FILTRO DE DISPONIBLES
            disponibles = [h for h in lista_hermanos if h not in reun['responsables']]
            options_with_empty = ["-- Sin asignar --"] + disponibles

            # PASO 2: ASIGNACIÓN AUDIO Y VIDEO
            st.markdown("**2️⃣ Asigna Audio, Video, Micrófono y Acomodador (Solo hermanos disponibles):**")
            st.caption(f"🟢 Quedan **{len(disponibles)}** hermanos disponibles.")

            col_a1, col_a2, col_a3, col_a4 = st.columns(4)

            def get_index(val, options):
                return options.index(val) if val in options else 0

            with col_a1:
                reun['audio'] = st.selectbox("Audio", options_with_empty, index=get_index(reun.get('audio', ''), options_with_empty), key=f"audio_{idx}")
            with col_a2:
                reun['video'] = st.selectbox("Video", options_with_empty, index=get_index(reun.get('video', ''), options_with_empty), key=f"video_{idx}")
            with col_a3:
                reun['mic'] = st.selectbox("Micrófono", options_with_empty, index=get_index(reun.get('mic', ''), options_with_empty), key=f"mic_{idx}")
            with col_a4:
                reun['acomodador'] = st.selectbox("Acomodador", options_with_empty, index=get_index(reun.get('acomodador', ''), options_with_empty), key=f"aco_{idx}")

            datos_programa_final.append({
                "Fecha": reun['fecha'],
                "Día": reun['dia'],
                "Audio": reun['audio'] if reun['audio'] != "-- Sin asignar --" else "",
                "Video": reun['video'] if reun['video'] != "-- Sin asignar --" else "",
                "Micrófono": reun['mic'] if reun['mic'] != "-- Sin asignar --" else "",
                "Acomodador": reun['acomodador'] if reun['acomodador'] != "-- Sin asignar --" else ""
            })

# --- 4. PLANTILLA HTML PARA VISTA PREVIA Y DESCARGAS ---
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
      <p>Congregación {congregacion} | {periodo_str}</p>
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
