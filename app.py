import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    page_title="Programa de Audio, Video y Salas",
    layout="wide"
)

st.title("📋 Generador de Programa de Audio, Video y Salas")

# --- 1. BARRA LATERAL (DATOS DE LA CONGREGACIÓN Y MESES) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    congregacion = st.text_input("Nombre de la Congregación", "El Gallito")
    periodo = st.text_input("Meses / Período", "Agosto y Septiembre 2026")
    
    st.markdown("---")
    st.subheader("👥 Lista de Hermanos")
    st.caption("Puedes agregar o quitar nombres de la lista desplegable:")
    
    # Lista predeterminada de hermanos para los desplegables
    lista_hermanos_defecto = [
        "--- NO HAY REUNIÓN ---",
        "José Pereira", "José Alberto González", "David Herrera", "Rodney Alfaro",
        "Carlos Josué Pereira", "Julio Sánchez", "Iván Zamora", "Josué López",
        "Javier García", "Dashler Sánchez", "Kenneth Solís", "Walter Sánchez",
        "Sebastián Montero", "Carlos Blanco", "Elixander Alvarado",
        "Geremy Fernández", "Rafael Segura", "Roger Loaiza", "Carlos Enrique Pereira"
    ]
    
    # Permitir al usuario modificar la lista maestra de hermanos si lo desea
    hermanos_texto = st.text_area("Hermanos disponibles (uno por línea)", value="\n".join(lista_hermanos_defecto), height=250)
    lista_hermanos = [h.strip() for h in hermanos_texto.split("\n") if h.strip()]

# --- 2. TABLA INTERACTIVA EDITABLE ---
st.subheader("✏️ Editar Asignaciones")
st.caption("Haz doble clic en cualquier celda para cambiar el nombre, fecha o asignación:")

# Datos iniciales para cargar en la tabla
data_inicial = [
    {"Fecha": "02/08/2026", "Día": "Domingo", "Audio": "José Pereira", "Video": "José Alberto González", "Micrófono": "David Herrera", "Acomodador": "Rodney Alfaro"},
    {"Fecha": "05/08/2026", "Día": "Miércoles", "Audio": "Carlos Josué Pereira", "Video": "Julio Sánchez", "Micrófono": "Iván Zamora", "Acomodador": "Josué López"},
    {"Fecha": "09/08/2026", "Día": "Domingo", "Audio": "Javier García", "Video": "Dashler Sánchez", "Micrófono": "Kenneth Solís", "Acomodador": "Walter Sánchez"},
    {"Fecha": "12/08/2026", "Día": "Miércoles", "Audio": "--- NO HAY REUNIÓN ---", "Video": "--- NO HAY REUNIÓN ---", "Micrófono": "--- NO HAY REUNIÓN ---", "Acomodador": "--- NO HAY REUNIÓN ---"},
    {"Fecha": "16/08/2026", "Día": "Domingo", "Audio": "--- NO HAY REUNIÓN ---", "Video": "--- NO HAY REUNIÓN ---", "Micrófono": "--- NO HAY REUNIÓN ---", "Acomodador": "--- NO HAY REUNIÓN ---"},
    {"Fecha": "18/08/2026", "Día": "Martes", "Audio": "Sebastián Montero", "Video": "Josué López", "Micrófono": "Carlos Blanco", "Acomodador": "Elixander Alvarado"},
    {"Fecha": "23/08/2026", "Día": "Domingo", "Audio": "Geremy Fernández", "Video": "José Alberto González", "Micrófono": "Rafael Segura", "Acomodador": "Roger Loaiza"},
    {"Fecha": "26/08/2026", "Día": "Miércoles", "Audio": "David Herrera", "Video": "Sebastián Montero", "Micrófono": "Rafael Segura", "Acomodador": "Carlos Enrique Pereira"},
    {"Fecha": "30/08/2026", "Día": "Domingo", "Audio": "Dashler Sánchez", "Video": "Carlos Josué Pereira", "Micrófono": "Walter Sánchez", "Acomodador": "Elixander Alvarado"},
]

df_inicial = pd.DataFrame(data_inicial)

# Editor interactivo tipo Excel dentro de Streamlit
df_editado = st.data_editor(
    df_inicial,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Fecha": st.column_config.TextColumn("Fecha", required=True),
        "Día": st.column_config.SelectboxColumn("Día", options=["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]),
        "Audio": st.column_config.SelectboxColumn("Audio", options=lista_hermanos),
        "Video": st.column_config.SelectboxColumn("Video", options=lista_hermanos),
        "Micrófono": st.column_config.SelectboxColumn("Micrófono", options=lista_hermanos),
        "Acomodador": st.column_config.SelectboxColumn("Acomodador", options=lista_hermanos),
    }
)

# --- 3. CONSTRUCCIÓN DEL HTML DINÁMICO ---
filas_html = ""
for _, row in df_editado.iterrows():
    is_no_reunion = (row['Audio'] == "--- NO HAY REUNIÓN ---")
    clase_td = ' class="no-hay-reunion"' if is_no_reunion else ''
    
    filas_html += f"""
    <tr>
        <td>{row['Fecha']}</td>
        <td>{row['Día']}</td>
        <td{clase_td}>{row['Audio']}</td>
        <td{clase_td}>{row['Video']}</td>
        <td{clase_td}>{row['Micrófono']}</td>
        <td{clase_td}>{row['Acomodador']}</td>
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
st.subheader("👁️ Vista Previa del Programa Generado")
components.html(html_code, height=750, scrolling=True)
