import streamlit as st
import pandas as pd
import random
import datetime

st.set_page_config(page_title="Programa Audio, Video y Salas", layout="centered")

st.title("📹 Generador de Programa: Audio, Video y Salas")
st.caption("Congregación Gallito, San José de la Montaña")

# 1. Base de Hermanos y Capacidades Configurada (Incluye a Iván Zamora)
hermanos_av = [
    "Carlos Josué Pereira", "Carlos Enrique Pereira", "José Pereira", "Josué López", 
    "Rodney Alfaro", "Geremy Fernández", "Julio Sánchez", "Dashler Sánchez", 
    "Sebastián Montero", "David Herrera", "José Alberto González", "Javier García", 
    "Elixander Alvarado", "Iván Zamora"
]

hermanos_solo_mics = ["Rafael Segura", "Kenneth Solís", "Walter Sánchez"]

# Lista EXCLUSIVA para Acomodadores (Ancianos y Siervos Ministeriales)
ancianos_y_ministeriales = [
    "Carlos Josué Pereira", "José Pereira", "Josué López", "Rodney Alfaro",
    "Geremy Fernández", "Julio Sánchez", "David Herrera", "José Alberto González",
    "Javier García"
]

# 2. Control de Fechas y Traslados
st.sidebar.header("⚙️ Configuración del Mes")
fecha = st.sidebar.date_input("Seleccione la fecha de la reunión")

es_septiembre_o_mas = fecha.month >= 9
visita_sc_pasada = fecha > datetime.date(2026, 8, 23)

disponibles_av = hermanos_av.copy()
if visita_sc_pasada and "Geremy Fernández" in disponibles_av:
    disponibles_av.remove("Geremy Fernández")

disponibles_mics = hermanos_solo_mics.copy()
if es_septiembre_o_mas:
    disponibles_mics.append("Iván Chavarría")

disponibles_acom = ancianos_y_ministeriales.copy()
if visita_sc_pasada and "Geremy Fernández" in disponibles_acom:
    disponibles_acom.remove("Geremy Fernández")

# 3. Formulario de Ocupados en el Programa
st.subheader("1. Selección de Ocupados")
ocupados = st.multiselect(
    "Marque los hermanos que tienen Presidencia, Lectura, Discurso o Partes en la reunión hoy:",
    options=sorted(list(set(disponibles_av + disponibles_mics)))
)

st.info("💡 Recordatorio: Oraciones y Limpieza NO se marcan aquí (los hermanos sí están disponibles para A/V).")

# 4. Generación con Prioridad Equilibrada
if st.button("🚀 Generar Programa"):
    libres_av = [h for h in disponibles_av if h not in ocupados]
    libres_mics = [h for h in (disponibles_av + disponibles_mics) if h not in ocupados]
    libres_acom = [h for h in disponibles_acom if h not in ocupados]
    
    if len(libres_av) >= 2 and len(libres_mics) >= 2 and len(libres_acom) >= 1:
        # Separar no ancianos para darles prioridad en A/V
        publicadores_av = [h for h in libres_av if h not in ancianos_y_ministeriales]
        ancianos_av = [h for h in libres_av if h in ancianos_y_ministeriales]
        
        # Mezclar priorizando publicadores
        pool_av = publicadores_av + ancianos_av
        equipo_av = random.sample(pool_av, 2)
        
        # Selección de 1 Micrófono (priorizando no ancianos restante)
        libres_mics_restantes = [h for h in libres_mics if h not in equipo_av]
        equipo_mics = random.sample(libres_mics_restantes, 1)
        
        # Selección de 1 Acomodador (solo ancianos/ministeriales sin repetir)
        libres_acom_restantes = [h for h in libres_acom if h not in equipo_av and h not in equipo_mics]
        
        if libres_acom_restantes:
            equipo_acom = random.sample(libres_acom_restantes, 1)
        else:
            equipo_acom = ["Requiere revisión manual"]

        # Crear tabla visual
        res_df = pd.DataFrame({
            "Función": [
                "Encargado de Audio",
                "Encargado de Video",
                "Plataforma y Micrófono",
                "Acomodador"
            ],
            "Hermano Asignado": [
                equipo_av[0],
                equipo_av[1],
                equipo_mics[0],
                equipo_acom[0]
            ]
        })
        
        st.success("¡Programa calculado con éxito!")
        st.table(res_df)
        
        # Descarga en CSV para Excel
        csv_data = res_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Programa (.csv para Excel)",
            data=csv_data,
            file_name=f"Programa_AV_{fecha}.csv",
            mime="text/csv"
        )
    else:
        st.error("No hay suficientes hermanos disponibles sin asignación previa en la lista.")
