import streamlit as st
import streamlit.components.v1 as components
import datetime
import calendar
import pandas as pd
import io

# Configuración de la página
st.set_page_config(
    page_title="Programa de Audio, Video, Micrófono y Acomodador",
    layout="wide"
)

st.title("📋 Generador de Programa de Audio, Video, Micrófono y Acomodador")

# --- DICCIONARIOS Y DÍAS ---
MESES_LISTA = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
MESES_DICT = {nombre: i + 1 for i, nombre in enumerate(MESES_LISTA)}
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_DESCANSO_MINIMO = 10  # Días mínimos entre asignaciones para un mismo hermano
MAX_ASIGNACIONES_MES = 2   # Máximo de asignaciones permitidas por mes por hermano

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

# --- 1. BARRA LATERAL (CONFIGURACIÓN Y CLASIFICACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración del Período")
    congregacion = st.text_input("Nombre de la Congregación", "El Gallito")
    
    anio = st.number_input("Año", min_value=2024, max_value=2035, value=2026, step=1)
    cant_meses = st.radio("Cantidad de Meses a programar:", ["1 Mes", "2 Meses"], index=0)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        mes_1 = st.selectbox("Mes 1", MESES_LISTA, index=8) # Septiembre
    
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
        st.session_state.periodo_cargado = (anio, tuple(meses_seleccionados), dia_habitual_entre_semana)
        st.success("¡Fechas cargadas correctamente!")
        st.rerun()

    # --- HISTORIAL PRECARGADO DE AGOSTO ---
    st.markdown("---")
    st.subheader("📂 Historial del Mes Anterior")
    
    historial_base_agosto = {
        "José Pereira": 2, "Javier García": 2, "Sebastián Montero": 2,
        "Kenneth Solís": 2, "Carlos Josué Pereira": 2, "Julio Sánchez": 1,
        "David Herrera": 3, "José Alberto González": 2, "Dáshler Sánchez": 2,
        "Elixander Alvarado": 2, "Rafael Segura": 2, "Carlos Enrique Pereira": 1,
        "Walter Sánchez": 1, "Rodney Alfaro": 2, "Josué López": 2,
        "Iván Zamora": 1, "Carlos Blanco": 1, "Geremy Fernández": 1, "Roger Loaiza": 1
    }

    fechas_base_agosto = {
        "Kenneth Solís": datetime.date(2026, 9, 2),
        "Josué López": datetime.date(2026, 9, 2),
        "José Alberto González": datetime.date(2026, 9, 2),
        "David Herrera": datetime.date(2026, 9, 2),
        "Javier García": datetime.date(2026, 8, 30),
        "Rodney Alfaro": datetime.date(2026, 8, 30),
        "Elixander Alvarado": datetime.date(2026, 8, 30),
        "Rafael Segura": datetime.date(2026, 8, 30),
        "Sebastián Montero": datetime.date(2026, 8, 26),
        "Dáshler Sánchez": datetime.date(2026, 8, 26),
        "Carlos Enrique Pereira": datetime.date(2026, 8, 26),
        "Carlos Josué Pereira": datetime.date(2026, 8, 23),
        "José Pereira": datetime.date(2026, 8, 23),
        "Iván Zamora": datetime.date(2026, 8, 23),
        "Walter Sánchez": datetime.date(2026, 8, 23),
        "Julio Sánchez": datetime.date(2026, 8, 19)
    }

    archivo_historial = st.file_uploader(
        "Sube un archivo adicional de historial (opcional Excel/CSV):",
        type=["xlsx", "xls", "csv"]
    )
    
    conteo_historial = historial_base_agosto.copy()
    
    if archivo_historial is not None:
        try:
            contenido = archivo_historial.read()
            df_hist = None

            try:
                dfs = pd.read_html(io.BytesIO(contenido))
                if dfs:
                    df_hist = dfs[0]
            except Exception:
                pass

            if df_hist is None:
                try:
                    df_hist = pd.read_csv(io.BytesIO(contenido))
                except Exception:
                    pass

            if df_hist is None:
                try:
                    df_hist = pd.read_excel(io.BytesIO(contenido))
                except Exception:
                    raise RuntimeError("Si usas archivos .xlsx nativos, instala 'openpyxl'.")

            for idx_row, row in df_hist.iterrows():
                row_str = row.astype(str).tolist()
                if any("Audio" in cell for cell in row_str) and any("Video" in cell for cell in row_str):
                    df_hist.columns = df_hist.iloc[idx_row]
                    df_hist = df_hist.iloc[idx_row + 1:].reset_index(drop=True)
                    break
                
            for col in ["Audio", "Video", "Micrófono", "Acomodador"]:
                if col in df_hist.columns:
                    for nombre in df_hist[col].dropna():
                        nom_str = str(nombre).strip()
                        if "Zamora" in nom_str:
                            nom_str = nom_str.replace("Zamora", "Chavarría")
                        if nom_str and "NO HAY" not in nom_str and nom_str != "-- Sin asignar --":
                            conteo_historial[nom_str] = conteo_historial.get(nom_str, 0) + 1
            st.success("¡Archivo de historial cargado!")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

    # --- CLASIFICACIÓN DE HERMANOS ---
    st.markdown("---")
    st.subheader("🔑 Clasificación de Cabina")

    # 1. Hermanos Locales con Llave y Experiencia (Supervisión / Video)
    locales_defecto = [
        "José Pereira",
        "Carlos Josué Pereira",
        "Julio Sánchez",
        "Javier García",
        "José Alberto González",
        "Sebastián Montero",
        "David Herrera",
        "Dáshler Sánchez",
        "Rodney Alfaro",
        "Kenneth Solís"
    ]
    locales_txt = st.text_area("🔑 Hermanos LOCALES (Experiencia / Video y Llave):", value="\n".join(locales_defecto), height=160)
    hermanos_locales = [h.strip() for h in locales_txt.split("\n") if h.strip()]

    # 2. Los 7 Nuevos integrantes a entrenar en Audio
    nuevos_defecto = [
        "Adiel Arias",
        "Fran Vega",
        "Meysson Pérez",
        "Yoiser Vargas",
        "Jossy Quesada",
        "Henry Altamirano",
        "Evans Arguedas"
    ]
    nuevos_txt = st.text_area("🌱 NUEVOS Integrantes (Audio / Entrenamiento):", value="\n".join(nuevos_defecto), height=160)
    hermanos_nuevos = [h.strip() for h in nuevos_txt.split("\n") if h.strip()]

    # 3. Acomodadores (ÚNICAMENTE Ancianos y Siervos Ministeriales)
    aco_defecto = [
        "Carlos Enrique Pereira",
        "Elixander Alvarado",
        "Walter Sánchez",
        "Rafael Segura",
        "José Pereira",
        "Julio Sánchez",
        "Javier García",
        "José Alberto González",
        "Rodney Alfaro"
    ]
    aco_txt = st.text_area("🚪 Acomodadores (SOLO Ancianos y Siervos Ministeriales):", value="\n".join(sorted(aco_defecto)), height=160)
    hermanos_aco = [h.strip() for h in aco_txt.split("\n") if h.strip()]

    # Total de integrantes para A/V
    hermanos_av = list(set(hermanos_locales + hermanos_nuevos))
    
    # Total de hermanos
    todos_hermanos = sorted(list(set(hermanos_av + hermanos_aco + ["Iván Chavarría", "Carlos Blanco"])))

    # Micrófonos
    mic_defecto = [h for h in todos_hermanos if h != "Carlos Enrique Pereira"]
    mic_txt = st.text_area("🎤 Autorizados para Micrófonos:", value="\n".join(mic_defecto), height=140)
    hermanos_mic = [h.strip() for h in mic_txt.split("\n") if h.strip()]

# --- 2. INICIALIZACIÓN Y ACTUALIZACIÓN DE SESIÓN ---
config_actual = (anio, tuple(meses_seleccionados), dia_habitual_entre_semana)

if "reuniones" not in st.session_state or st.session_state.get("periodo_cargado") != config_actual:
    st.session_state.reuniones = generar_fechas_meses(
        anio=anio,
        meses_seleccionados=meses_seleccionados,
        dia_entre_semana=dia_habitual_entre_semana
    )
    st.session_state.periodo_cargado = config_actual

st.subheader(f"🗓️ Asignación de Ocupados por Fecha — {periodo_str}")
st.info("💚 **Límite de Equilibrio Familiar Activo:** Ningún hermano tendrá más de **2 asignaciones al mes** para asegurar su descanso y convivencia.")

datos_programa_final = []

conteo_acumulado = {h: conteo_historial.get(h, 0) for h in todos_hermanos}
ultimo_puesto_av = {h: None for h in hermanos_av}
ultimo_tipo_dia_mic = {h: None for h in hermanos_mic}
ultima_fecha_asignado = {h: fechas_base_agosto.get(h, None) for h in todos_hermanos}

# Diccionario para controlar el máximo de 2 asignaciones por mes por hermano
# Estructura: {(hermano, 'YYYY-MM'): cantidad}
conteo_mes_actual = {}

# --- 3. ALGORITMO DE ASIGNACIÓN CON CONTROL MÁXIMO DE 2/MES ---
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
            
            excluidos = set(reun['responsables'])
            es_domingo = (reun['dia'] == "Domingo")
            tipo_dia_actual = "Domingo" if es_domingo else "EntreSemana"
            
            try:
                dt_obj = datetime.datetime.strptime(reun['fecha'], "%d/%m/%Y").date()
                clave_mes = dt_obj.strftime("%Y-%m")
            except Exception:
                dt_obj = datetime.date(anio, 1, 1)
                clave_mes = "actual"

            # Función para filtrar hermanos que ya alcanzaron el tope mensual (2 asignaciones)
            def esta_disponible_mes(hermano):
                cant = conteo_mes_actual.get((hermano, clave_mes), 0)
                return cant < MAX_ASIGNACIONES_MES

            def score_candidato(hermano, es_mic=False):
                dias_desde_ultimo = 999
                if ultima_fecha_asignado.get(hermano) is not None:
                    dias_desde_ultimo = (dt_obj - ultima_fecha_asignado[hermano]).days
                
                penalizacion_descanso = 5000 if dias_desde_ultimo < DIAS_DESCANSO_MINIMO else 0
                conteo_mes = conteo_mes_actual.get((hermano, clave_mes), 0)
                conteo_gen = conteo_acumulado.get(hermano, 0)
                
                repeticion_dia = 0
                if es_mic and ultimo_tipo_dia_mic.get(hermano) == tipo_dia_actual:
                    repeticion_dia = 5
                    
                # Se prioriza al que tenga menos asignaciones en el mes actual y general
                return (penalizacion_descanso, conteo_mes, conteo_gen, repeticion_dia)

            def registrar_asignacion(hermano, puesto):
                if hermano:
                    excluidos.add(hermano)
                    conteo_acumulado[hermano] = conteo_acumulado.get(hermano, 0) + 1
                    conteo_mes_actual[(hermano, clave_mes)] = conteo_mes_actual.get((hermano, clave_mes), 0) + 1
                    ultima_fecha_asignado[hermano] = dt_obj

            # 1. ASIGNAR AUDIO (Nuevos integrantes)
            cand_audio = [h for h in hermanos_nuevos if h not in excluidos and esta_disponible_mes(h)]
            if not cand_audio: # Fallback si todos los nuevos completaron sus 2 turnos
                cand_audio = [h for h in hermanos_nuevos if h not in excluidos]
            if not cand_audio:
                cand_audio = [h for h in hermanos_av if h not in excluidos]
                
            cand_audio.sort(key=lambda h: score_candidato(h))
            h_audio = cand_audio[0] if cand_audio else ""
            registrar_asignacion(h_audio, "Audio")

            # 2. ASIGNAR VIDEO (Hermano local experimentado con llave)
            cand_video = [h for h in hermanos_locales if h not in excluidos and esta_disponible_mes(h)]
            if not cand_video:
                cand_video = [h for h in hermanos_locales if h not in excluidos]
            if not cand_video:
                cand_video = [h for h in hermanos_av if h not in excluidos]
                
            cand_video.sort(key=lambda h: score_candidato(h))
            h_video = cand_video[0] if cand_video else ""
            registrar_asignacion(h_video, "Video")

            # 3. ASIGNAR MICRÓFONO
            candidatos_mic = [h for h in hermanos_mic if h not in excluidos and h != "Carlos Enrique Pereira" and esta_disponible_mes(h)]
            
            if not es_domingo:
                candidatos_mic = [h for h in candidatos_mic if h not in ["Carlos Blanco", "Walter Sánchez"]]

            if not candidatos_mic:
                candidatos_mic = [h for h in todos_hermanos if h not in excluidos and h != "Carlos Enrique Pereira" and esta_disponible_mes(h)]
                if not es_domingo:
                    candidatos_mic = [h for h in candidatos_mic if h not in ["Carlos Blanco", "Walter Sánchez"]]

            # Si ya se agotaron los que tienen menos de 2 en el mes, se permite fallback
            if not candidatos_mic:
                candidatos_mic = [h for h in hermanos_mic if h not in excluidos and h != "Carlos Enrique Pereira"]

            candidatos_mic.sort(key=lambda h: score_candidato(h, es_mic=True))

            h_mic = candidatos_mic[0] if candidatos_mic else ""
            if h_mic:
                registrar_asignacion(h_mic, "Micrófono")
                ultimo_tipo_dia_mic[h_mic] = tipo_dia_actual

            # 4. ASIGNAR ACOMODADOR (Exclusivamente Ancianos y Siervos Ministeriales)
            candidatos_aco = [h for h in hermanos_aco if h not in excluidos and esta_disponible_mes(h)]
            if not candidatos_aco:
                candidatos_aco = [h for h in hermanos_aco if h not in excluidos]
            if not candidatos_aco:
                candidatos_aco = [h for h in hermanos_aco]

            candidatos_aco.sort(key=lambda h: score_candidato(h))
            h_aco = candidatos_aco[0] if candidatos_aco else ""
            registrar_asignacion(h_aco, "Acomodador")

            st.caption(f"🤖 **Asignación:** Audio: *{h_audio}* | Video: *{h_video}* | Mic: *{h_mic}* | Acomodador: *{h_aco}*")

            datos_programa_final.append({
                "Fecha": reun['fecha'],
                "Día": reun['dia'],
                "Audio": h_audio,
                "Video": h_video,
                "Micrófono": h_mic,
                "Acomodador": h_aco
            })

# --- 4. VISTA PREVIA Y DESCARGAS ---
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
      <h1>PROGRAMA DE AUDIO, VIDEO, MICRÓFONO Y ACOMODADOR</h1>
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
        enlace.download = 'Programa_Audio_Video_Microfono_Acomodador.png';
        enlace.href = canvas.toDataURL('image/png');
        enlace.click();
      }});
    }}

    function descargarPDF() {{
      const elemento = document.getElementById('contenedor-programa');
      const opciones = {{
        margin: 0.3,
        filename: 'Programa_Audio_Video_Microfono_Acomodador.pdf',
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
      XLSX.writeFile(libro, 'Programa_Audio_Video_Microfono_Acomodador.xlsx');
    }}
  </script>
</body>
</html>
"""

st.markdown("---")
st.subheader("👁️ Vista Previa Final")
components.html(html_code, height=750, scrolling=True)
