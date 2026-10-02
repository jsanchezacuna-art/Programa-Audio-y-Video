import calendar
import datetime as dt
import html
import io
import uuid

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Programa de Audio, Video, Micrófono y Acomodador",
    layout="wide",
)

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
NUMERO_MES = {nombre: numero for numero, nombre in enumerate(MESES, start=1)}
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
NUMERO_DIA = {nombre: numero for numero, nombre in enumerate(DIAS)}

# Estas tres reglas nunca se relajan. Si no existe alguien elegible, el puesto queda sin asignar.
DIAS_DESCANSO_MINIMO = 10
MAX_ASIGNACIONES_MES = 2
SIN_ASIGNAR = "⚠ SIN ASIGNAR"
SIN_REUNION = "--- NO HAY REUNIÓN ---"
PUESTOS = ["Audio", "Video", "Micrófono", "Acomodador"]


def clave_reunion(fecha):
    """Una clave estable: los widgets no se mezclan al borrar una reunión."""
    return f"reunion-{fecha.isoformat()}-{uuid.uuid4().hex[:8]}"


def crear_reunion(fecha):
    return {
        "id": clave_reunion(fecha),
        "fecha": fecha,
        "sin_reunion": False,
        "responsables": [],
    }


def generar_reuniones(anio, meses, dia_entre_semana):
    fechas = []
    objetivo = NUMERO_DIA[dia_entre_semana]

    for nombre_mes in meses:
        mes = NUMERO_MES[nombre_mes]
        ultimo_dia = calendar.monthrange(anio, mes)[1]

        for dia in range(1, ultimo_dia + 1):
            fecha = dt.date(anio, mes, dia)
            if fecha.weekday() in (objetivo, NUMERO_DIA["Domingo"]):
                fechas.append(fecha)

    return [crear_reunion(fecha) for fecha in sorted(fechas)]


def normalizar_nombre(valor):
    nombre = str(valor).strip()
    return nombre.replace("Zamora", "Chavarría")


def es_nombre_asignable(valor):
    texto = normalizar_nombre(valor)

    return bool(
        texto
        and texto.lower() not in {
            "nan",
            "none",
            "-- sin asignar --",
            SIN_ASIGNAR.lower(),
        }
        and "NO HAY" not in texto.upper()
    )


def fecha_desde_valor(valor):
    try:
        fecha = pd.to_datetime(valor, dayfirst=True, errors="coerce")

        if pd.isna(fecha):
            return None

        return fecha.date()

    except (TypeError, ValueError):
        return None


def leer_historial(archivo):
    """Lee conteos y última fecha por persona desde CSV, Excel o HTML."""
    contenido = archivo.getvalue()
    nombre = archivo.name.lower()
    tabla = None
    errores = []

    lectores = []

    if nombre.endswith((".xlsx", ".xls")):
        lectores = [lambda: pd.read_excel(io.BytesIO(contenido))]
    elif nombre.endswith(".csv"):
        lectores = [lambda: pd.read_csv(io.BytesIO(contenido))]
    elif nombre.endswith((".html", ".htm")):
        lectores = [lambda: pd.read_html(io.BytesIO(contenido))[0]]

    for lector in lectores:
        try:
            tabla = lector()
            break
        except Exception as exc:
            errores.append(str(exc))

    if tabla is None:
        detalle = errores[-1] if errores else "Formato no compatible"
        raise ValueError(f"No se pudo leer el archivo: {detalle}")

    tabla.columns = [str(columna).strip() for columna in tabla.columns]

    # Algunos HTML tienen los encabezados dentro de la tabla.
    for indice, fila in tabla.iterrows():
        valores = [str(valor).strip() for valor in fila.tolist()]

        if "Audio" in valores and "Video" in valores:
            tabla.columns = valores
            tabla = tabla.iloc[indice + 1:].reset_index(drop=True)
            break

    columnas = {str(columna).strip().lower(): columna for columna in tabla.columns}
    columna_fecha = columnas.get("fecha")

    conteos = {}
    ultimas_fechas = {}

    for _, fila in tabla.iterrows():
        fecha = fecha_desde_valor(fila[columna_fecha]) if columna_fecha else None

        for puesto in PUESTOS:
            columna = columnas.get(puesto.lower())

            if columna is None:
                continue

            nombre_hermano = fila[columna]

            if not es_nombre_asignable(nombre_hermano):
                continue

            hermano = normalizar_nombre(nombre_hermano)
            conteos[hermano] = conteos.get(hermano, 0) + 1

            if fecha and (
                hermano not in ultimas_fechas
                or fecha > ultimas_fechas[hermano]
            ):
                ultimas_fechas[hermano] = fecha

    return conteos, ultimas_fechas


def lista_desde_area(texto):
    return sorted(
        {
            normalizar_nombre(linea)
            for linea in texto.splitlines()
            if normalizar_nombre(linea)
        }
    )


def clave_mes(fecha):
    return fecha.strftime("%Y-%m")


def candidato_valido(
    hermano,
    fecha,
    asignados_hoy,
    conteos_mes,
    ultimas_fechas,
):
    if hermano in asignados_hoy:
        return False

    if conteos_mes.get((hermano, clave_mes(fecha)), 0) >= MAX_ASIGNACIONES_MES:
        return False

    ultima = ultimas_fechas.get(hermano)

    return ultima is None or (fecha - ultima).days >= DIAS_DESCANSO_MINIMO


def escoger(
    candidatos,
    fecha,
    asignados_hoy,
    conteos_mes,
    conteos_totales,
    ultimas_fechas,
    parejas_historial,
    ultimo_tipo_mic=None,
    tipo_dia=None,
):
    elegibles = [
        hermano
        for hermano in candidatos
        if candidato_valido(
            hermano,
            fecha,
            asignados_hoy,
            conteos_mes,
            ultimas_fechas,
        )
    ]

    def puntaje(hermano):
        repeticiones_pareja = sum(
            tuple(sorted((hermano, otro))) in parejas_historial
            for otro in asignados_hoy
        )

        misma_clase_mic = (
            1
            if ultimo_tipo_mic is not None
            and ultimo_tipo_mic.get(hermano) == tipo_dia
            else 0
        )

        return (
            conteos_mes.get((hermano, clave_mes(fecha)), 0),
            conteos_totales.get(hermano, 0),
            repeticiones_pareja,
            misma_clase_mic,
            hermano.casefold(),
        )

    return min(elegibles, key=puntaje) if elegibles else None


def registrar(
    hermano,
    fecha,
    asignados_hoy,
    conteos_mes,
    conteos_totales,
    ultimas_fechas,
    parejas_historial,
):
    for otro in asignados_hoy:
        parejas_historial.add(tuple(sorted((hermano, otro))))

    asignados_hoy.add(hermano)
    conteos_totales[hermano] = conteos_totales.get(hermano, 0) + 1
    conteos_mes[(hermano, clave_mes(fecha))] = (
        conteos_mes.get((hermano, clave_mes(fecha)), 0) + 1
    )
    ultimas_fechas[hermano] = fecha


st.title("📋 Generador de Programa de Audio, Video, Micrófono y Acomodador")

with st.sidebar:
    st.header("⚙️ Configuración del período")

    congregacion = st.text_input(
        "Nombre de la congregación",
        "El Gallito",
    )

    anio = st.number_input(
        "Año",
        min_value=2024,
        max_value=2035,
        value=2026,
        step=1,
    )

    cantidad_meses = st.radio(
        "Cantidad de meses",
        ["1 Mes", "2 Meses"],
        horizontal=True,
    )

    mes_1 = st.selectbox("Mes 1", MESES, index=9)
    meses = [mes_1]

    if cantidad_meses == "2 Meses":
        opciones_mes_2 = [mes for mes in MESES if mes != mes_1]
        predeterminado = MESES[(MESES.index(mes_1) + 1) % 12]

        mes_2 = st.selectbox(
            "Mes 2",
            opciones_mes_2,
            index=opciones_mes_2.index(predeterminado),
        )

        meses.append(mes_2)

    dia_semana = st.selectbox(
        "Día habitual entre semana",
        ["Miércoles", "Martes", "Jueves", "Lunes"],
    )

    periodo = (
        f"{meses[0]} {anio}"
        if len(meses) == 1
        else f"{meses[0]} y {meses[1]} {anio}"
    )

    st.caption(f"Período activo: {periodo}")

    configuracion = (int(anio), tuple(meses), dia_semana)

    if st.button(
        "🔄 Cargar fechas del período",
        use_container_width=True,
    ):
        st.session_state.reuniones = generar_reuniones(*configuracion)
        st.session_state.configuracion_reuniones = configuracion
        st.rerun()

    st.divider()
    st.subheader("📂 Historial")

    archivo_historial = st.file_uploader(
        "Archivo anterior (Excel, CSV o HTML)",
        type=["xlsx", "xls", "csv", "html", "htm"],
    )

    conteos_historial = {}
    fechas_historial = {}

    if archivo_historial is not None:
        try:
            conteos_historial, fechas_historial = leer_historial(
                archivo_historial
            )
            st.success(
                f"Historial leído: {len(conteos_historial)} personas."
            )

        except ValueError as error:
            st.error(str(error))

    st.divider()
    st.subheader("🔑 Personas autorizadas")

    nuevos = [
        "Adiel Arias",
        "Fran Vega",
        "Meysson Pérez",
        "Yoiser Vargas",
        "Jossy Quesada",
        "Henry Altamirano",
        "Evans Arguedas",
        "José Alberto González",
    ]

    video_defecto = sorted(
        {
            "José Pereira",
            "Carlos Josué Pereira",
            "Julio Sánchez",
            "Javier García",
            "Sebastián Montero",
            "David Herrera",
            "Dáshler Sánchez",
            "Rodney Alfaro",
            "Kenneth Solís",
            "Josué López",
            "Adiel Arias",
            "Fran Vega",
            "Meysson Pérez",
            "Yoiser Vargas",
            "Jossy Quesada",
            "Henry Altamirano",
            "Evans Arguedas",
        }
    )

    audio_defecto = sorted(set(nuevos + ["Dáshler Sánchez"]))

    acomodador_defecto = sorted(
        {
            "Carlos Enrique Pereira",
            "Elixander Alvarado",
            "Walter Sánchez",
            "Rafael Segura",
            "José Pereira",
            "Julio Sánchez",
            "Rodney Alfaro",
            "Adiel Arias",
            "Fran Vega",
            "Meysson Pérez",
            "Yoiser Vargas",
            "Jossy Quesada",
            "Henry Altamirano",
            "Evans Arguedas",
        }
    )

    video = lista_desde_area(
        st.text_area(
            "🖥️ Video",
            "\n".join(video_defecto),
            height=180,
        )
    )

    audio = lista_desde_area(
        st.text_area(
            "🎙️ Audio",
            "\n".join(audio_defecto),
            height=145,
        )
    )

    acomodador = lista_desde_area(
        st.text_area(
            "🚪 Acomodador",
            "\n".join(acomodador_defecto),
            height=170,
        )
    )

    todos = sorted(
        set(
            video
            + audio
            + acomodador
            + ["Iván Chavarría", "Carlos Blanco"]
        )
    )

    microfono_defecto = [
        hermano
        for hermano in todos
        if hermano not in {
            "Carlos Enrique Pereira",
            "José Alberto González",
        }
    ]

    microfono = lista_desde_area(
        st.text_area(
            "🎤 Micrófono",
            "\n".join(microfono_defecto),
            height=160,
        )
    )

if (
    "reuniones" not in st.session_state
    or st.session_state.get("configuracion_reuniones") != configuracion
):
    st.session_state.reuniones = generar_reuniones(*configuracion)
    st.session_state.configuracion_reuniones = configuracion

st.subheader(f"🗓️ Reuniones y responsables — {periodo}")

st.info(
    f"Reglas strictly: autorización por puesto, una asignación por reunión, "
    f"{DIAS_DESCANSO_MINIMO} días de descanso y máximo "
    f"{MAX_ASIGNACIONES_MES} asignaciones mensuales. "
    "Si no hay candidato válido, se mostrará SIN ASIGNAR."
)

for reunion in st.session_state.reuniones:
    identificador = reunion["id"]
    fecha = reunion["fecha"]

    with st.expander(
        f"📅 {fecha.strftime('%d/%m/%Y')} ({DIAS[fecha.weekday()]})",
        expanded=True,
    ):
        columna_fecha, columna_cancelar, columna_borrar = st.columns([3, 3, 1])

        with columna_fecha:
            nueva_fecha = st.date_input(
                "Fecha de la reunión",
                value=fecha,
                key=f"fecha-{identificador}",
            )
            reunion["fecha"] = nueva_fecha

        with columna_cancelar:
            reunion["sin_reunion"] = st.checkbox(
                "🚫 Cancelar reunión / asamblea",
                value=reunion["sin_reunion"],
                key=f"cancelar-{identificador}",
            )

        with columna_borrar:
            st.write("")

            if st.button(
                "🗑️",
                key=f"borrar-{identificador}",
                help="Quitar esta reunión",
            ):
                st.session_state.reuniones = [
                    item
                    for item in st.session_state.reuniones
                    if item["id"] != identificador
                ]
                st.rerun()

        reunion["responsables"] = st.multiselect(
            "🙋‍♂️ Ocupados con responsabilidades principales",
            todos,
            default=[
                hermano
                for hermano in reunion["responsables"]
                if hermano in todos
            ],
            key=f"ocupados-{identificador}",
        )

# El cálculo empieza desde cero en cada ejecución.
conteos_totales = dict(conteos_historial)
ultimas_fechas = dict(fechas_historial)
conteos_mes = {}
parejas_historial = set()
ultimo_tipo_mic = {hermano: None for hermano in microfono}
filas = []

for reunion in sorted(
    st.session_state.reuniones,
    key=lambda item: item["fecha"],
):
    fecha = reunion["fecha"]
    dia = DIAS[fecha.weekday()]

    if reunion["sin_reunion"]:
        filas.append(
            {
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Día": dia,
                **{puesto: SIN_REUNION for puesto in PUESTOS},
            }
        )
        continue

    excluidos = set(reunion["responsables"])

    # David Herrera no se programa los domingos.
    if dia == "Domingo":
        excluidos.add("David Herrera")

    asignados = set(excluidos)
    resultado = {}
    tipo_dia = "Domingo" if dia == "Domingo" else "Entre semana"

    reglas = [
        ("Audio", audio),
        ("Video", video),
        (
            "Micrófono",
            [
                hermano
                for hermano in microfono
                if not (
                    dia != "Domingo"
                    and hermano in {"Carlos Blanco", "Walter Sánchez"}
                )
            ],
        ),
        ("Acomodador", acomodador),
    ]

    for puesto, autorizados in reglas:
        candidatos = [
            hermano
            for hermano in autorizados
            if hermano not in excluidos
        ]

        hermano = escoger(
            candidatos,
            fecha,
            asignados,
            conteos_mes,
            conteos_totales,
            ultimas_fechas,
            parejas_historial,
            ultimo_tipo_mic if puesto == "Micrófono" else None,
            tipo_dia,
        )

        if hermano is None:
            resultado[puesto] = SIN_ASIGNAR

        else:
            resultado[puesto] = hermano

            registrar(
                hermano,
                fecha,
                asignados,
                conteos_mes,
                conteos_totales,
                ultimas_fechas,
                parejas_historial,
            )

            if puesto == "Micrófono":
                ultimo_tipo_mic[hermano] = tipo_dia

    filas.append(
        {
            "Fecha": fecha.strftime("%d/%m/%Y"),
            "Día": dia,
            **resultado,
        }
    )

pendientes = [
    fila
    for fila in filas
    if SIN_ASIGNAR in fila.values()
]

if pendientes:
    st.warning(
        f"Hay {len(pendientes)} reunión(es) con puestos sin asignar. "
        "Revisa disponibilidades o las reglas."
    )

datos = pd.DataFrame(
    filas,
    columns=["Fecha", "Día", *PUESTOS],
)

st.subheader("👁️ Vista previa final")
st.dataframe(datos, use_container_width=True, hide_index=True)

filas_html = "".join(
    "<tr>"
    + "".join(
        f"<td>{html.escape(str(fila[columna]))}</td>"
        for columna in datos.columns
    )
    + "</tr>"
    for fila in filas
)

encabezados_html = "".join(
    f"<th>{html.escape(columna)}</th>"
    for columna in datos.columns
)

nombre_seguro = html.escape(congregacion)
periodo_seguro = html.escape(periodo)

html_programa = f"""
<!doctype html>
<html lang='es'>
<head>
<meta charset='utf-8'>

<script src='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'></script>
<script src='https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js'></script>
<script src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js'></script>

<style>
body {{
    font-family: Arial, sans-serif;
    background: #f4f6f9;
    margin: 0;
    padding: 12px;
    text-align: center;
}}

button {{
    border: 0;
    border-radius: 6px;
    color: #fff;
    cursor: pointer;
    font-weight: bold;
    margin: 0 5px 16px;
    padding: 10px 16px;
}}

#png {{ background: #2b5876; }}
#pdf {{ background: #c9403b; }}
#excel {{ background: #18733a; }}

#programa {{
    background: #fff;
    border: 1px solid #d0d7de;
    box-shadow: 0 4px 12px #0002;
    margin: auto;
    max-width: 1000px;
}}

header {{
    background: #224b7a;
    color: #fff;
    padding: 24px 12px;
}}

h1 {{
    font-size: 20px;
    letter-spacing: .7px;
    margin: 0 0 8px;
}}

p {{
    margin: 0;
}}

.tabla {{
    overflow-x: auto;
    padding: 15px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

th {{
    background: #34495e;
    color: #fff;
}}

th, td {{
    border: 1px solid #e1e8ed;
    font-size: 13px;
    padding: 9px 6px;
    text-align: center;
}}

tr:nth-child(even) {{
    background: #f8fafc;
}}
</style>
</head>

<body>
<button id='png' onclick='imagen()'>📷 Descargar PNG</button>
<button id='pdf' onclick='pdf()'>📄 Descargar PDF</button>
<button id='excel' onclick='excel()'>📊 Descargar Excel</button>

<main id='programa'>
    <header>
        <h1>PROGRAMA DE AUDIO, VIDEO, MICRÓFONO Y ACOMODADOR</h1>
        <p>Congregación {nombre_seguro} | {periodo_seguro}</p>
    </header>

    <div class='tabla'>
        <table>
            <thead>
                <tr>{encabezados_html}</tr>
            </thead>
            <tbody>
                {filas_html}
            </tbody>
        </table>
    </div>
</main>

<script>
async function imagen() {{
    await document.fonts.ready;

    html2canvas(
        document.querySelector('#programa'),
        {{
            scale: 2,
            backgroundColor: '#fff'
        }}
    ).then(canvas => {{
        const enlace = document.createElement('a');
        enlace.download = 'Programa.png';
        enlace.href = canvas.toDataURL();
        enlace.click();
    }});
}}

function pdf() {{
    html2pdf()
        .set({{
            margin: .3,
            filename: 'Programa.pdf',
            html2canvas: {{ scale: 2 }},
            jsPDF: {{
                unit: 'in',
                format: 'letter',
                orientation: 'landscape'
            }}
        }})
        .from(document.querySelector('#programa'))
        .save();
}}

function excel() {{
    const libro = XLSX.utils.table_to_book(
        document.querySelector('table'),
        {{ sheet: 'Programa' }}
    );

    XLSX.writeFile(libro, 'Programa.xlsx');
}}
</script>
</body>
</html>
"""

components.html(html_programa, height=700, scrolling=True)

st.download_button(
    "⬇️ Descargar tabla CSV",
    datos.to_csv(index=False).encode("utf-8-sig"),
    file_name="Programa_Audio_Video_Microfono_Acomodador.csv",
    mime="text/csv",
)
