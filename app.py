import streamlit as st
import streamlit.components.v1 as components
import datetime
import calendar
import pandas as pd

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

def generar_fechas_meses(anio, meses_seleccionados, dia_entre_semana="Miércoles"):
    dias_map = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}
    target_midweek = dias_map.get(dia_entre_semana, 2)
    reuniones_generadas = []
    
    for mes_nombre in meses_seleccionados:
        mes_num = MESES_DICT[mes_nombre]
        num_dias = calendar.monthrange(anio, mes_num)[1]
        
        for dia in range(1, num_dias + 1):
            dt = datetime.date(anio, mes_num, dia)
            if dt.weekday() == target_midweek:
                reuniones_generadas.append({
                    "dt": dt,
                    "fecha": dt.strftime("%d/%m/%Y"),
                    "dia": dia_entre_semana,
                    "sin_reunion": False,
                    "responsables": []
                })
            elif dt.weekday() == 6:
                reuniones_generadas.append({
                    "dt": dt,
                    "fecha": dt.strftime("%d/%m/%Y"),
                    "dia": "Domingo",
                    "sin_reunion": False,
                    "responsables": []
                })
                
    reuniones_generadas.sort(key=lambda x: x["dt"])
    return reuniones_generadas

# --- 1. BARRA LATERAL (CONFIGURACIÓN Y LISTAS POR PRIVILEGIO) ---
with st.sidebar:
    st.header("⚙️ Configuración del Período")
    congregacion = st.text_input("Nombre de la Congregación", "El Gallito")
    
    anio = st.number_input("Año", min_value=2024, max_value=2035, value=2026, step=1)
    cant_meses = st.radio("Cantidad de Meses a programar:", ["1 Mes", "2 Meses"], index=1)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        mes_1 = st.selectbox("Mes 1", MESES_LISTA, index=7)
    
    meses_seleccionados = [mes_1]
    if cant_meses == "2 Meses":
        with col_m2:
            idx_m2 = (MESES_LISTA.index(mes_1) + 1) % 12
            mes_2 = st.selectbox("Mes 2", MESES_LISTA, index=idx_m2)
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

    # --- CARGA DE HISTORIAL ANTERIOR ---
    st.markdown("---")
    st.subheader("📂 Historial del Mes Anterior")
    archivo_historial = st.file_uploader(
        "Sube el programa anterior (Excel/CSV) para rotación:",
        type=["xlsx", "xls", "csv"]
    )
    
    conteo_historial = {}
    if archivo_historial is not None:
        try:
            if archivo_historial.name.endswith(".csv"):
                df_hist = pd.read_csv(archivo_historial)
            else:
                df_hist = pd.read_excel(archivo_historial)
                
            for col in ["Audio", "Video", "Micrófono", "Acomodador"]:
                if col in df_hist.columns:
                    for nombre in df_hist[col].dropna():
                        nom_str = str(nombre).strip()
                        if nom_str and "NO HAY" not in nom_str and nom_str != "-- Sin asignar --":
                            conteo_historial[nom_str] = conteo_historial.get(nom_str, 0) + 1
            st.success(f"¡Historial cargado con éxito!")
        except Exception:
            st.error("Error al leer el archivo.")

    # --- CLASIFICACIÓN DE HERMANOS POR PRIVILEGIO ---
    st.markdown("---")
    st.subheader("👥 Hermanos Autorizados por Puesto")
    st.caption("Ajusta los nombres en cada grupo según los privilegios/aptitudes correspondientes:")

    # 1. Audio y Video
    av_defecto = ["José Pereira", "José Alberto González", "Carlos Josué Pereira", "Javier García", "Sebastián Montero", "David Herrera"]
    av_txt = st.text_area("🎧🖥️ Autorizados para Audio y Video:", value="\n".join(av_defecto), height=110)
    hermanos_av = [h.strip() for h in av_txt.split("\n") if h.strip()]

    # 2. Micrófonos
    mic_defecto = ["Iván Zamora", "Carlos Blanco", "Kenneth Solís", "Elixander Alvarado", "Geremy Fernández", "Rafael Segura"]
    mic_txt = st.text_area("🎤 Autorizados para Micrófonos:", value="\n".join(mic_defecto), height=110)
    hermanos_mic = [h.strip() for h in mic_txt.split("\n") if h.strip()]

    # 3. Acomodadores
    aco_defecto = ["Rodney Alfaro", "Josué López", "Walter Sánchez", "Julio Sánchez", "Dashler Sánchez", "Roger Loaiza", "Carlos Enrique Pereira"]
    aco_txt = st.text_area("🚪 Autorizados para Acomodadores:", value="\n".join(aco_defecto), height=110)
    hermanos_aco = [h.strip() for h in aco_txt.split("\n") if h.strip()]

    # Todos los hermanos combinados para seleccionar los "ocupados"
    todos_hermanos = sorted(list(set(hermanos_av + hermanos_mic + hermanos_aco)))

# --- 2. INICIALIZACIÓN DE SESIÓN ---
if "reuniones" not in st.session_state or len(st.session_state.reuniones) == 0:
    st.session_state.reuniones = generar_fechas_meses(
        anio=anio,
        meses_seleccionados=meses_seleccionados,
        dia_entre_semana=dia_habitual_entre_semana
    )

st.subheader(f"🗓️ Asignación de Ocupados por Fecha — {periodo_str}")
st.info("👉 Selecciona los hermanos que tienen **presidencia, discursos, plataforma, etc.** El sistema asignará **Audio/Video, Micrófono y Acomodador únicamente entre los hermanos autorizados para cada puesto**.")

datos_programa_final = []
conteo_acumulado = {h: conteo_historial.get(h, 0) for h in todos_hermanos}

# --- 3. PROCESAMIENTO Y ASIGNACIÓN SEGÚN REGLAS DE PRIVILEGIO ---
for idx, reun in enumerate(st.session_state.reuniones):
    with st.expander(f"📅 #{idx+1} — {reun['fecha']} ({reun['dia']})", expanded=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 3, 1])
        
        with col_f1:
            reun['fecha'] = st.text_input("Fecha", value=reun['fecha'], key=f"fecha_{idx}")
        with col_f2:
            idx_dia = DIAS_SEMANA.index(reun['dia']) if reun['dia'] in DIAS_SEMANA else 2
            reun['dia'] = st.selectbox("Día de la reunión", DIAS_SEMANA, index=idx_dia, key=f"dia_{idx}")
        with col_f3:
            reun['sin_reunion'] = st.checkbox("🚫 CANCELAR SEMANA / ASAMBLEA", value=reun['sin_reunion'], key=f"sin_reunion_{idx}")
        with col_f4:
            st.write("")
            st.write("")
            if st.button("🗑️", key=f"del_{idx}"):
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
            resp_validos = [h for h in reun.get('responsables', []) if h in todos_hermanos]
            reun['responsables'] = st.multiselect(
                "🙋‍♂️ Ocupados con responsabilidades principales ese día:",
                options=todos_hermanos,
                default=resp_validos,
                key=f"resp_{idx}"
            )
            
            ocupados = set(reun['responsables'])

            # Auxiliar para seleccionar el hermano disponible con menor número de asignaciones
            def seleccionar_hermano(lista_base, excluidos):
                candidatos = [h for h in lista_base if h not in excluidos]
                if not candidatos:
                    # Si no hay candidatos exclusivos, busca en la lista general de disponibles
                    candidatos = [h for h in todos_hermanos if h not in excluidos]
                if candidatos:
                    candidatos.sort(key=lambda h: conteo_acumulado.get(h, 0))
                    return candidatos[0]
                return ""

            excluidos_actuales = set(ocupados)

            # 1. Asignar Audio (desde lista AV)
            h_audio = seleccionar_hermano(hermanos_av, excluidos_actuales)
            if h_audio: excluidos_actuales.add(h_audio)

            # 2. Asignar Video (desde lista AV)
            h_video = seleccionar_hermano(hermanos_av, excluidos_actuales)
            if h_video: excluidos_actuales.add(h_video)

            # 3. Asignar Micrófono (desde lista MIC)
            h_mic = seleccionar_hermano(hermanos_mic, excluidos_actuales)
            if h_mic: excluidos_actuales.add(h_mic)

            # 4. Asignar Acomodador (desde lista ACO)
            h_aco = seleccionar_hermano(hermanos_aco, excluidos_actuales)
            if h_aco: excluidos_actuales.add(h_aco)

            # Actualizar conteo acumulado
            for h_asig in [h_audio, h_video, h_mic, h_aco]:
                if h_asig:
                    conteo_acumulado[h_asig] = conteo_acumulado.get(h_asig, 0) + 1

            st.caption(f"🤖 **Asignado respetando privilegios:** Audio: *{h_audio}* | Video: *{h_video}* | Mic: *{h_mic}* | Acomodador: *{h_aco}*")

            datos_programa_final.append({
                "Fecha": reun['fecha'],
                "Día": reun['dia'],
                "Audio": h_audio,
                "Video": h_video,
                "Micrófono": h_mic,
                "Acomodador": h_aco
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
