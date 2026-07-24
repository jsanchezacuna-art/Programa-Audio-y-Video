import streamlit as st
import pandas as pd
import random
import datetime
import io

st.set_page_config(page_title="Programa Audio, Video y Salas", layout="centered")

st.title("📹 Generador de Programa: Audio, Video y Salas")
st.caption("Congregación Gallito, San José de la Montaña")

# 1. Base de Hermanos y Capacidades Configurada (Actualizada)
hermanos_av = [
    "Carlos Josué Pereira", "José Pereira", "Josué López", "Rodney Alfaro",
    "Geremy Fernández", "Julio Sánchez", "Dashler Sánchez", "Sebastián Montero",
    "David Herrera", "José Alberto González", "Javier García", "Elixander Alvarado"
]

hermanos_solo_mics = ["Rafael Segura", "Kenneth Solís", "Walter Sánchez"]

# 2. Control de Fechas y Traslados
st.sidebar.header("⚙️ Configuración del Mes")
fecha = st.sidebar.date_input("Seleccione la fecha de la reunión")

# Corrección de comparación de fechas usando datetime.date
es_septiembre_o_mas = fecha.month >= 9
visita_sc_pasada = fecha > datetime.date(2026, 8, 23)

# Control por traslado de Geremy Fernández tras la visita del SC
disponibles_av = hermanos_av.copy()
if visita_sc_pasada and "Geremy Fernández" in disponibles_av:
    disponibles_av.remove("Geremy Fernández")

disponibles_mics = hermanos_solo_mics.copy()
if es_septiembre_o_mas:
    disponibles_mics.append("Iván Chavarría")

# 3. Formulario de Ocupados en el Programa
st.subheader("1. Selección de Ocupados")
ocupados = st.multiselect(
    "Marque los hermanos que tienen Presidencia, Lectura, Discurso o Partes activas hoy:",
    options=sorted(list(set(disponibles_av + disponibles_mics)))
)

st.info("💡 Recordatorio: Las personas asignadas a Oración o Limpieza NO deben marcarse aquí (sí están disponibles).")

# 4. Generación y Exportación
if st.button("🚀 Generar Programa y Exportar"):
    libres_av = [h for h in disponibles_av if h not in ocupados]
    libres_mics = [h for h in (disponibles_av + disponibles_mics) if h not in ocupados]
    
    if len(libres_av) >= 2 and len(libres_mics) >= 3:
        equipo_av = random.sample(libres_av, 2)
        
        # Evitar duplicar en la misma reunión
        libres_mics_restantes = [h for h in libres_mics if h not in equipo_av]
        
        # Validación de cantidad de libres para micrófonos y acomodador
        num_mics = min(2, len(libres_mics_restantes))
        equipo_mics = random.sample(libres_mics_restantes, num_mics)
        
        libres_acom = [h for h in libres_mics_restantes if h not in equipo_mics]
        equipo_acom = random.sample(libres_acom, 1) if libres_acom else ["Sin asignar"]

        puestos = ["Encargado de Audio", "Encargado de Video"]
        asignados = [equipo_av[0], equipo_av[1]]

        for i, m in enumerate(equipo_mics):
            puestos.append(f"Plataforma y Micrófonos {i+1}")
            asignados.append(m)

        puestos.append("Acomodador")
        asignados.append(equipo_acom[0])

        # Matriz para la tabla
        res_df = pd.DataFrame({
            "Función": puestos,
            "Hermano Asignado": asignados
        })
        
        st.success("¡Programa calculado con éxito!")
        st.table(res_df)
        
        # Botón para descargar directo a Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            res_df.to_excel(writer, index=False, sheet_name='Asignaciones')
            
        st.download_button(
            label="📥 Descargar Tabla para Excel",
            data=buffer.getvalue(),
            file_name=f"Programa_AV_{fecha}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No hay suficientes hermanos disponibles sin asignación previa en la lista.")
