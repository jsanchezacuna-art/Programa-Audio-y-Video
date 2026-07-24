import streamlit as st
import pandas as pd
import random
import datetime
import calendar
from collections import Counter

st.set_page_config(page_title="Programa Audio, Video y Salas", layout="centered")

st.title("📅 Generador Mensual: Audio, Video y Salas")
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

# Acomodadores (Ancianos, SM + Elixander Alvarado + Roger Loaiza + Carlos Enrique Pereira + Walter Sánchez)
ancianos_y_ministeriales = [
    "Carlos Josué Pereira", "Carlos Enrique Pereira", "José Pereira", "Josué López", "Rodney Alfaro",
    "Geremy Fernández", "Julio Sánchez", "David Herrera", "José Alberto González",
    "Javier García", "Elixander Alvarado", "Roger Loaiza", "Walter Sánchez"
]

# Fecha límite de la visita del SC (23 de Agosto de 2026)
FECHA_VISITA_SC = datetime.date(2026, 8, 23)

# 2. Selección de Mes, Año y Duración
st.sidebar.header("⚙️ Configuración del Programa")
anio = st.sidebar.number_input("Año", min_value=2026, max_value=2030, value=2026)
mes_nombres = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
mes_sel = st.sidebar.selectbox("Seleccione el Mes de Inicio", mes_nombres, index=6)
num_mes = mes_nombres.index(mes_sel) + 1

duracion = st.sidebar.radio("¿Cuántos meses desea generar?", ["1 Mes", "2 Meses"], index=0)

# Obtener fechas de reunión (Miércoles/Martes y Domingos)
def obtener_fechas_mes(m_num, a_num):
    n_dias = calendar.monthrange(a_num, m_num)[1]
    f_lista = []
    for dia in range(1, n_dias + 1):
        f_dt = datetime.date(a_num, m_num, dia)
        if f_dt.weekday() in [2, 6]: # 2 = Miércoles, 6 = Domingo
            f_lista.append(f_dt)
    return f_lista

fechas_reunion = obtener_fechas_mes(num_mes, anio)

# Si se seleccionaron 2 meses, agregar el mes siguiente
if duracion == "2 Meses":
    siguiente_mes = num_mes + 1 if num_mes < 12 else 1
    siguiente_anio = anio if num_mes < 12 else anio + 1
    fechas_reunion += obtener_fechas_mes(siguiente_mes, siguiente_anio)

texto_rango = f"{mes_sel} {anio}" if duracion == "1 Mes" else f"{mes_sel} y {mes_nombres[(num_mes % 12)]} {anio}"
st.subheader(f"🗓️ Reuniones para {texto_rango}: {len(fechas_reunion)} fechas encontradas")

# 3. Formulario para marcar ocupados, cambio de día (Visita SC) o cancelaciones
st.write("Seleccione el estado de cada reunión, ajuste días por visita del SC o marque los no disponibles:")

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
            if dia_real == "Martes":
                fecha_efectiva = f - datetime.timedelta(days=1)
            else:
                fecha_efectiva = f
        else:
            dia_real = "Domingo"
            fecha_efectiva = f
            
        dias_ajustados_por_fecha[f] = (dia_real, fecha_efectiva)
        
        es_cancelada = st.checkbox(f"❌ Cancelar esta reunión (Asamblea / Sin reunión)", key=f"canc_{f}")
        canceladas_por_fecha[f] = es_cancelada
        
        if not es_cancelada:
            visita_sc_pasada = fecha_efectiva > FECHA_VISITA_SC
            es_septiembre_o_mas = fecha_efectiva.month >= 9
            
            # Filtrar hermanos que se van después de la visita (Geremy y Roger)
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

def seleccionar_equilibrado(lista_candidatos, contador_usos, cantidad=1):
    if not lista_candidatos:
        return []
    
    candidatos_validos = []
    for h in lista_candidatos:
        if h == "Roger Loaiza" and contador_usos[h] >= 1:
            continue
        candidatos_validos.append(h)
        
    if not candidatos_validos:
        return []
    
    candidatos_ordenados = sorted(candidatos_validos, key=lambda h: (contador_usos[h], random.random()))
    seleccionados = candidatos_ordenados[:cantidad]
    return seleccionados

# 4. Generación del Programa Mensual / Bimestral
if st.button("🚀 Generar Programa Completo"):
    filas_programa = []
    error_detectado = False
    
    contador_usos = Counter()
    
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
            continue

        visita_sc_pasada = fecha_efectiva > FECHA_VISITA_SC
        es_septiembre_o_mas = fecha_efectiva.month >= 9
        
        # Aplicar bajas de la congregación automáticamente tras la visita
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
            equipo_av = seleccionar_equilibrado(libres_av, contador_usos, cantidad=2)
            for h in equipo_av:
                contador_usos[h] += 1
            
            libres_mics_restantes = [h for h in libres_mics if h not in equipo_av]
            equipo_mics = seleccionar_equilibrado(libres_mics_restantes, contador_usos, cantidad=1)
            for h in equipo_mics:
                contador_usos[h] += 1
            
            libres_acom_restantes = [h for h in libres_acom if h not in equipo_av and h not in equipo_mics]
            equipo_acom = seleccionar_equilibrado(libres_acom_restantes, contador_usos, cantidad=1)
            if equipo_acom:
                contador_usos[equipo_acom[0]] += 1
            else:
                equipo_acom = ["Revisar manual"]
            
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
        st.success(f"¡Programa generado con éxito para {texto_rango}!")

# 5. Sección de Visualización, Edición Manual y Descarga
if st.session_state["programa_guardado"] is not None:
    st.divider()
    st.subheader("📝 Edición Manual y Descarga del Programa")
    st.info("💡 Puedes hacer doble clic sobre cualquier casilla de la tabla para cambiar un hermano manualmente si lo necesitas.")
    
    df_editable = st.data_editor(
        st.session_state["programa_guardado"], 
        use_container_width=True,
        num_rows="fixed"
    )
    
    csv_data = df_editable.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Descargar Programa Final (.csv)",
        data=csv_data,
        file_name=f"Programa_AV_{mes_sel}_{anio}.csv",
        mime="text/csv"
    )
