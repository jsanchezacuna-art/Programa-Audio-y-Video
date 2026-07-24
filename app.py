import streamlit as st
import pandas as pd
import random
import datetime
import calendar

st.set_page_config(page_title="Programa Audio, Video y Salas", layout="centered")

st.title("📅 Generador Mensual: Audio, Video y Salas")
st.caption("Congregación Gallito, San José de la Montaña")

# 1. Base de Hermanos por Rol Exacto

# Audio y Video (Sin Carlos Blanco ni Elixander Alvarado)
hermanos_av = [
    "Carlos Josué Pereira", "Carlos Enrique Pereira", "José Pereira", "Josué López", 
    "Rodney Alfaro", "Geremy Fernández", "Julio Sánchez", "Dashler Sánchez", 
    "Sebastián Montero", "David Herrera", "José Alberto González", "Javier García"
]

# Exclusivos/dedicados a micrófonos y apoyo
hermanos_solo_mics = [
    "Rafael Segura", "Kenneth Solís", "Walter Sánchez", 
    "Iván Zamora", "Carlos Blanco", "Elixander Alvarado"
]

# Acomodadores (Ancianos, Siervos Ministeriales + Elixander Alvarado)
ancianos_y_ministeriales = [
    "Carlos Josué Pereira", "José Pereira", "Josué López", "Rodney Alfaro",
    "Geremy Fernández", "Julio Sánchez", "David Herrera", "José Alberto González",
    "Javier García", "Elixander Alvarado"
]

# 2. Selección de Mes y Año
st.sidebar.header("⚙️ Configuración del Mes")
anio = st.sidebar.number_input("Año", min_value=2026, max_value=2030, value=2026)
mes_nombres = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
mes_sel = st.sidebar.selectbox("Seleccione el Mes", mes_nombres, index=6)
num_mes = mes_nombres.index(mes_sel) + 1

# Obtener todos los miércoles (2) y domingos (6) del mes seleccionado
num_dias = calendar.monthrange(anio, num_mes)[1]
fechas_reunion = []

for dia in range(1, num_dias + 1):
    fecha_dt = datetime.date(anio, num_mes, dia)
    if fecha_dt.weekday() in [2, 6]: # 2 = Miércoles, 6 = Domingo
        fechas_reunion.append(fecha_dt)

st.subheader(f"🗓️ Reuniones para {mes_sel} {anio}: {len(fechas_reunion)} fechas encontradas")

# 3. Formulario para marcar ocupados o cancelar por asamblea
st.write("Seleccione el estado de cada reunión o marque los ocupados:")

ocupados_por_fecha = {}
canceladas_por_fecha = {}

with st.expander("📌 Configurar fechas del mes (Ocupados y Cancelaciones)", expanded=True):
    for f in fechas_reunion:
        dia_semana = "Miércoles" if f.weekday() == 2 else "Domingo"
        etiqueta = f"{dia_semana} {f.strftime('%d/%m/%Y')}"
        
        st.markdown(f"### 🗓️ {etiqueta}")
        
        # Checkbox para cancelar la reunión por asamblea
        es_cancelada = st.checkbox(f"❌ Cancelar esta reunión (Asamblea / Sin reunión)", key=f"canc_{f}")
        canceladas_por_fecha[f] = es_cancelada
        
        if not es_cancelada:
            visita_sc_pasada = f > datetime.date(2026, 8, 23)
            es_septiembre_o_mas = f.month >= 9
            
            disp_av = hermanos_av.copy()
            if visita_sc_pasada and "Geremy Fernández" in disp_av:
                disp_av.remove("Geremy Fernández")
                
            disp_mics = disp_av + hermanos_solo_mics
            if es_septiembre_o_mas:
                disp_mics.append("Iván Chavarría")

            opciones_totales = sorted(list(set(disp_av + disp_mics)))
            
            ocupados_por_fecha[f] = st.multiselect(
                f"Hermanos ocupados el {etiqueta}:",
                options=opciones_totales,
                key=f.strftime("%Y-%m-%d")
            )
        else:
            ocupados_por_fecha[f] = []
        
        st.divider()

# 4. Generación del Programa Mensual
if st.button("🚀 Generar Programa Completo del Mes"):
    filas_programa = []
    error_detectado = False
    
    for f in fechas_reunion:
        dia_nombre = "Miércoles" if f.weekday() == 2 else "Domingo"
        
        # Si la reunión se canceló
        if canceladas_por_fecha[f]:
            filas_programa.append({
                "Fecha": f.strftime("%d/%m/%Y"),
                "Día": dia_nombre,
                "Audio": "--- NO HAY REUNIÓN ---",
                "Video": "--- NO HAY REUNIÓN ---",
                "Micrófono": "--- NO HAY REUNIÓN ---",
                "Acomodador": "--- NO HAY REUNIÓN ---"
            })
            continue

        visita_sc_pasada = f > datetime.date(2026, 8, 23)
        es_septiembre_o_mas = f.month >= 9
        
        d_av = hermanos_av.copy()
        if visita_sc_pasada and "Geremy Fernández" in d_av:
            d_av.remove("Geremy Fernández")
            
        d_mics = d_av + hermanos_solo_mics
        if es_septiembre_o_mas:
            d_mics.append("Iván Chavarría")
            
        d_acom = ancianos_y_ministeriales.copy()
        if visita_sc_pasada and "Geremy Fernández" in d_acom:
            d_acom.remove("Geremy Fernández")
            
        ocupados_hoy = ocupados_por_fecha[f]
        
        libres_av = [h for h in d_av if h not in ocupados_hoy]
        libres_mics = [h for h in d_mics if h not in ocupados_hoy]
        libres_acom = [h for h in d_acom if h not in ocupados_hoy]
        
        if len(libres_av) >= 2 and len(libres_mics) >= 1 and len(libres_acom) >= 1:
            publicadores_av = [h for h in libres_av if h not in ancianos_y_ministeriales]
            ancianos_av = [h for h in libres_av if h in ancianos_y_ministeriales]
            pool_av = publicadores_av + ancianos_av
            equipo_av = random.sample(pool_av, 2)
            
            libres_mics_restantes = [h for h in libres_mics if h not in equipo_av]
            equipo_mics = random.sample(libres_mics_restantes, 1)
            
            libres_acom_restantes = [h for h in libres_acom if h not in equipo_av and h not in equipo_mics]
            equipo_acom = random.sample(libres_acom_restantes, 1) if libres_acom_restantes else ["Revisar manual"]
            
            filas_programa.append({
                "Fecha": f.strftime("%d/%m/%Y"),
                "Día": dia_nombre,
                "Audio": equipo_av[0],
                "Video": equipo_av[1],
                "Micrófono": equipo_mics[0],
                "Acomodador": equipo_acom[0]
            })
        else:
            st.error(f"Faltan hermanos disponibles para la fecha {f.strftime('%d/%m/%Y')}.")
            error_detectado = True

    if not error_detectado and len(filas_programa) == len(fechas_reunion):
        res_df = pd.DataFrame(filas_programa)
        
        st.success(f"¡Programa de {mes_sel} {anio} generado con éxito!")
        st.dataframe(res_df, use_container_width=True)
        
        csv_data = res_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Descargar Programa Completo de {mes_sel} (.csv)",
            data=csv_data,
            file_name=f"Programa_AV_{mes_sel}_{anio}.csv",
            mime="text/csv"
        )
