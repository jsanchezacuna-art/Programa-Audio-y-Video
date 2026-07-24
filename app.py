import streamlit as st
import pandas as pd
import random
import datetime
import calendar
from collections import Counter
import io

# Importación de ReportLab para exportar a PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

st.set_page_config(page_title="Programa Audio, Video y Salas", layout="centered")

st.title("📅 Generador Avanzado: Audio, Video y Salas")
st.caption("Congregación Gallito, San José de la Montaña")

# Inicializar historial en memoria de la sesión
if "programa_guardado" not in st.session_state:
    st.session_state["programa_guardado"] = None

# 1. Base de Hermanos por Rol Exacto

# Audio y Video
hermanos_av = [
    "Carlos Josué Pereira", "José Pereira", "Josué López", 
    "Rodney Alfaro", "Geremy Fernández", "Julio Sánchez", "Dashler Sánchez", 
    "Sebastián Montero", "David Herrera", "José Alberto González", "Javier García"
]

# Exclusivos/dedicados a micrófonos y apoyo (Carlos Blanco solo aquí)
hermanos_solo_mics = [
    "Rafael Segura", "Kenneth Solís", "Walter Sánchez", 
    "Iván Zamora", "Carlos Blanco", "Elixander Alvarado"
]

# Acomodadores
ancianos_y_ministeriales = [
    "Carlos Josué Pereira", "Carlos Enrique Pereira", "José Pereira", "Josué López", "Rodney Alfaro",
    "Geremy Fernández", "Julio Sánchez", "David Herrera", "José Alberto González",
    "Javier García", "Elixander Alvarado", "Roger Loaiza", "Walter Sánchez"
]

FECHA_VISITA_SC = datetime.date(2026, 8, 23)

# 2. Selección de Mes, Año y Opciones
st.sidebar.header("⚙️ Configuración del Programa")
anio = st.sidebar.number_input("Año", min_value=2026, max_value=2030, value=2026)
mes_nombres = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
mes_sel = st.sidebar.selectbox("Seleccione el Mes de Inicio", mes_nombres, index=6)
num_mes = mes_nombres.index(mes_sel) + 1

duracion = st.sidebar.radio("¿Cuántos meses desea generar?", ["1 Mes", "2 Meses"], index=0)

# Carga de Historial Anterior (Mejora 3)
st.sidebar.divider()
st.sidebar.header("📂 Historial Anterior")
archivo_historial = st.sidebar.file_uploader("Cargar CSV del mes anterior (Opcional)", type=["csv"])

hermanos_recientes = []
if archivo_historial is not None:
    try:
        df_ant = pd.read_csv(archivo_historial)
        if not df_ant.empty:
            # Tomar la última fila válida del mes anterior
            ultima_fila = df_ant.iloc[-1]
            for col in ["Audio", "Video", "Micrófono", "Acomodador"]:
                if col in df_ant.columns and "---" not in str(ultima_fila[col]):
                    hermanos_recientes.append(ultima_fila[col])
            st.sidebar.success("¡Historial anterior cargado con éxito!")
    except Exception:
        st.sidebar.warning("No se pudo leer el archivo de historial.")

# Obtener fechas
def obtener_fechas_mes(m_num, a_num):
    n_dias = calendar.monthrange(a_num, m_num)[1]
    f_lista = []
    for dia in range(1, n_dias + 1):
        f_dt = datetime.date(a_num, m_num, dia)
        if f_dt.weekday() in [2, 6]:
            f_lista.append(f_dt)
    return f_lista

fechas_reunion = obtener_fechas_mes(num_mes, anio)
if duracion == "2 Meses":
    sig_mes = num_mes + 1 if num_mes < 12 else 1
    sig_anio = anio if num_mes < 12 else anio + 1
    fechas_reunion += obtener_fechas_mes(sig_mes, sig_anio)

texto_rango = f"{mes_sel} {anio}" if duracion == "1 Mes" else f"{mes_sel} y {mes_nombres[(num_mes % 12)]} {anio}"
st.subheader(f"🗓️ Reuniones para {texto_rango}: {len(fechas_reunion)} fechas encontradas")

# 3. Formulario para marcar ocupados, cambio de día o cancelaciones
ocupados_por_fecha = {}
canceladas_por_fecha = {}
dias_ajustados_por_fecha = {}

with st.expander("📌 Configurar fechas del mes (Ocupados, Visita SC y Cancelaciones)", expanded=True):
    for f in fechas_reunion:
        es_miercoles = f.weekday() == 2
        dia_semana_defecto = "Miércoles" if es_miercoles else "Domingo"
        etiqueta_base = f"{dia_semana_defecto} {f.strftime('%d/%m/%Y')}"
        
        st.markdown(f"### 🗓️ {etiqueta_base}")
        
        if es_miercoles:
            dia_real = st.radio(
                f"Día de la reunión de entre semana (Visita SC):",
                options=["Miércoles", "Martes"],
                index=0,
                key=f"dia_real_{f}",
                horizontal=True
            )
            fecha_efectiva = f - datetime.timedelta(days=1) if dia_real == "Martes" else f
        else:
            dia_real = "Domingo"
            fecha_efectiva = f
            
        dias_ajustados_por_fecha[f] = (dia_real, fecha_efectiva)
        
        es_cancelada = st.checkbox(f"❌ Cancelar esta reunión (Asamblea / Sin reunión)", key=f"canc_{f}")
        canceladas_por_fecha[f] = es_cancelada
        
        if not es_cancelada:
            visita_sc_pasada = fecha_efectiva > FECHA_VISITA_SC
            es_septiembre_o_mas = fecha_efectiva.month >= 9
            
            disp_av = hermanos_av.copy()
            if visita_sc_pasada and "Geremy Fernández" in disp_av:
                disp_av.remove("Geremy Fernández")
                
            disp_mics = disp_av + hermanos_solo_mics
            if es_septiembre_o_mas:
                disp_mics.append("Iván Chavarría")

            disp_acom = ancianos_y_ministeriales.copy()
            if visita_sc_pasada:
                if "Geremy Fernández" in disp_acom:
                    disp_acom.remove("Geremy Fernández")
                if "Roger Loaiza" in disp_acom:
                    disp_acom.remove("Roger Loaiza")

            opciones_totales = sorted(list(set(disp_av + disp_mics + disp_acom)))
            
            ocupados_por_fecha[f] = st.multiselect(
                f"Hermanos NO disponibles el {dia_real} {fecha_efectiva.strftime('%d/%m/%Y')}:",
                options=opciones_totales,
                key=f.strftime("%Y-%m-%d")
            )
        else:
            ocupados_por_fecha[f] = []
        
        st.divider()

def seleccionar_equilibrado(lista_candidatos, contador_usos, ultimos_asignados, cantidad=1):
    if not lista_candidatos:
        return []
    
    candidatos_validos = []
    for h in lista_candidatos:
        if h == "Roger Loaiza" and contador_usos[h] >= 1:
            continue
        candidatos_validos.append(h)
        
    if not candidatos_validos:
        return []
    
    # Penalizar a hermanos asignados en la reunión inmediatamente anterior
    def peso_prioridad(h):
        penalizacion_reciente = 2.0 if h in ultimos_asignados else 0.0
        return (contador_usos[h] + penalizacion_reciente, random.random())
    
    candidatos_ordenados = sorted(candidatos_validos, key=peso_prioridad)
    return candidatos_ordenados[:cantidad]

# 4. Generación del Programa
if st.button("🚀 Generar Programa Completo"):
    filas_programa = []
    error_detectado = False
    contador_usos = Counter()
    ultimos_asignados = hermanos_recientes.copy()
    
    for f in fechas_reunion:
        dia_nombre, fecha_efectiva = dias_ajustados_por_fecha[f]
        fecha_txt = fecha_efectiva.strftime("%d/%m/%Y")
        
        if canceladas_por_fecha[f]:
            filas_programa.append({
                "Fecha": fecha_txt,
                "Día": dia_nombre,
                "Audio": "--- NO HAY REUNIÓN ---",
                "Video": "--- NO HAY REUNIÓN ---",
                "Micrófono": "--- NO HAY REUNIÓN ---",
                "Acomodador": "--- NO HAY REUNIÓN ---"
            })
            ultimos_asignados = []
            continue

        visita_sc_pasada = fecha_efectiva > FECHA_VISITA_SC
        es_septiembre_o_mas = fecha_efectiva.month >= 9
        
        d_av = hermanos_av.copy()
        if visita_sc_pasada and "Geremy Fernández" in d_av:
            d_av.remove("Geremy Fernández")
            
        d_mics = d_av + hermanos_solo_mics
        if es_septiembre_o_mas:
            d_mics.append("Iván Chavarría")
            
        d_acom = ancianos_y_ministeriales.copy()
        if visita_sc_pasada:
            if "Geremy Fernández" in d_acom:
                d_acom.remove("Geremy Fernández")
            if "Roger Loaiza" in d_acom:
                d_acom.remove("Roger Loaiza")
            
        ocupados_hoy = ocupados_por_fecha[f]
        
        libres_av = [h for h in d_av if h not in ocupados_hoy]
        libres_mics = [h for h in d_mics if h not in ocupados_hoy]
        libres_acom = [h for h in d_acom if h not in ocupados_hoy]
        
        if len(libres_av) >= 2 and len(libres_mics) >= 1 and len(libres_acom) >= 1:
            equipo_av = seleccionar_equilibrado(libres_av, contador_usos, ultimos_asignados, cantidad=2)
            for h in equipo_av:
                contador_usos[h] += 1
            
            libres_mics_restantes = [h for h in libres_mics if h not in equipo_av]
            equipo_mics = seleccionar_equilibrado(libres_mics_restantes, contador_usos, ultimos_asignados, cantidad=1)
            for h in equipo_mics:
                contador_usos[h] += 1
            
            libres_acom_restantes = [h for h in libres_acom if h not in equipo_av and h not in equipo_mics]
            equipo_acom = seleccionar_equilibrado(libres_acom_restantes, contador_usos, ultimos_asignados, cantidad=1)
            if equipo_acom:
                contador_usos[equipo_acom[0]] += 1
            else:
                equipo_acom = ["Revisar manual"]
            
            asig_hoy = equipo_av + equipo_mics + equipo_acom
            ultimos_asignados = asig_hoy
            
            filas_programa.append({
                "Fecha": fecha_txt,
                "Día": dia_nombre,
                "Audio": equipo_av[0],
                "Video": equipo_av[1],
                "Micrófono": equipo_mics[0],
                "Acomodador": equipo_acom[0]
            })
        else:
            st.error(f"Faltan hermanos disponibles para la fecha {fecha_txt}.")
            error_detectado = True

    if not error_detectado and len(filas_programa) == len(fechas_reunion):
        st.session_state["programa_guardado"] = pd.DataFrame(filas_programa)
        st.session_state["contador_usos"] = contador_usos
        st.success(f"¡Programa generado con éxito para {texto_rango}!")

# 5. Visualización, Edición, Alertas y Exportación
if st.session_state["programa_guardado"] is not None:
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📝 Edición y Tabla", "📆 Vista de Calendario", "📊 Alertas y Equilibrio"])
    
    with tab1:
        st.subheader("📝 Edición Manual del Programa")
        st.info("💡 Haz doble clic sobre cualquier casilla para modificar una asignación.")
        
        df_editable = st.data_editor(
            st.session_state["programa_guardado"], 
            use_container_width=True,
            num_rows="fixed"
        )
        st.session_state["programa_guardado"] = df_editable

    with tab2:
        # Mejora 2: Vista previa tipo calendario
        st.subheader(f"📆 Calendario de Asignaciones: {texto_rango}")
        for idx, row in df_editable.iterrows():
            with st.container():
                st.markdown(f"**📌 {row['Día']} {row['Fecha']}**")
                if "---" in row['Audio']:
                    st.caption("❌ Reunión cancelada")
                else:
                    col_a, col_v, col_m, col_ac = st.columns(4)
                    col_a.metric("Audio", row['Audio'])
                    col_v.metric("Video", row['Video'])
                    col_m.metric("Micrófono", row['Micrófono'])
                    col_ac.metric("Acomodador", row['Acomodador'])
                st.divider()

    with tab3:
        # Mejora 4: Panel de Alertas de equilibrio
        st.subheader("📊 Control y Alertas de Equilibrio")
        c_usos = st.session_state.get("contador_usos", Counter())
        
        todos_hermanos = sorted(list(set(hermanos_av + hermanos_solo_mics + ancianos_y_ministeriales)))
        hermanos_sin_asignar = [h for h in todos_hermanos if c_usos[h] == 0]
        
        if hermanos_sin_asignar:
            st.warning(f"⚠️ **Hermanos con 0 asignaciones en el periodo:** {', '.join(hermanos_sin_asignar)}")
        else:
            st.success("✅ Todos los hermanos disponibles participan activamente en este periodo.")
            
        df_conteo = pd.DataFrame(list(c_usos.items()), columns=["Hermano", "Asignaciones"]).sort_values(by="Asignaciones", ascending=False)
        st.table(df_conteo)

    # Botones de descarga
    st.divider()
    col_csv, col_pdf = st.columns(2)
    
    csv_data = df_editable.to_csv(index=False).encode('utf-8')
    col_csv.download_button(
        label=f"📥 Descargar CSV (Excel)",
        data=csv_data,
        file_name=f"Programa_AV_{mes_sel}_{anio}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Mejora 1: Generador de PDF
    if PDF_DISPONIBLE:
        def generar_pdf(df):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()
            
            titulo_style = ParagraphStyle(
                'TituloStyle',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=1,
                spaceAfter=12
            )
            
            elements.append(Paragraph(f"<b>PROGRAMA DE AUDIO, VIDEO Y SALAS</b>", titulo_style))
            elements.append(Paragraph(f"Congregación Gallito - {texto_rango}", styles['Normal']))
            elements.append(Spacer(1, 15))
            
            datos_tabla = [["Fecha", "Día", "Audio", "Video", "Micrófono", "Acomodador"]]
            for _, row in df.iterrows():
                datos_tabla.append([row['Fecha'], row['Día'], row['Audio'], row['Video'], row['Micrófono'], row['Acomodador']])
                
            t = Table(datos_tabla, colWidths=[65, 65, 110, 110, 100, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F4E78')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            
            elements.append(t)
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()

        pdf_bytes = generar_pdf(df_editable)
        col_pdf.download_button(
            label=f"📄 Descargar PDF Listo para Imprimir",
            data=pdf_bytes,
            file_name=f"Programa_AV_{mes_sel}_{anio}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
