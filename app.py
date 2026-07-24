<!DOCTYPE html>
<html lang="es">
<head>
  <!-- CODER CORRECTO PARA EVITAR CARACTERES RARS (TILDES Y Ñ) -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Programa de Audio, Video y Salas</title>

  <!-- LIBRERÍAS EXTERNAS PARA DESCARGAS -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

  <style>
    body {
      font-family: Arial, Helvetica, sans-serif;
      background-color: #f4f6f9;
      margin: 0;
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    /* BARRA DE BOTONES DE DESCARGA */
    .panel-descargas {
      margin-bottom: 20px;
      display: flex;
      gap: 15px;
    }

    .btn-descarga {
      padding: 10px 18px;
      font-size: 14px;
      font-weight: bold;
      color: #ffffff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: background-color 0.2s ease;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn-imagen { background-color: #2b5876; }
    .btn-imagen:hover { background-color: #1e3c50; }

    .btn-pdf { background-color: #d9534f; }
    .btn-pdf:hover { background-color: #c9302c; }

    .btn-excel { background-color: #1e7e34; }
    .btn-excel:hover { background-color: #145a23; }

    /* CONTENEDOR PRINCIPAL DEL PROGRAMA */
    #contenedor-programa {
      width: 100%;
      max-width: 1100px;
      background-color: #ffffff;
      border: 1px solid #d0d7de;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      padding: 0 0 20px 0;
      box-sizing: border-box;
    }

    /* ENCABEZADO AZUL */
    .header-banner {
      background-color: #224b7a;
      color: #ffffff;
      text-align: center;
      padding: 30px 20px;
    }

    .header-banner h1 {
      margin: 0 0 10px 0;
      font-size: 20px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-weight: 600;
    }

    .header-banner p {
      margin: 0;
      font-size: 14px;
      opacity: 0.9;
    }

    /* TABLA */
    .tabla-contenedor {
      padding: 20px;
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      color: #333333;
    }

    th {
      background-color: #34495e;
      color: #ffffff;
      font-weight: bold;
      padding: 12px 8px;
      text-align: center;
      border: 1px solid #34495e;
    }

    td {
      padding: 10px 8px;
      text-align: center;
      border-bottom: 1px solid #e1e8ed;
      border-right: 1px solid #e1e8ed;
      border-left: 1px solid #e1e8ed;
    }

    tr:nth-child(even) {
      background-color: #f8fafc;
    }

    .no-hay-reunion {
      font-weight: bold;
      color: #555555;
      letter-spacing: 1px;
    }
  </style>
</head>
<body>

  <!-- BARRA DE ACCIONES / BOTONES -->
  <div class="panel-descargas">
    <button class="btn-descarga btn-imagen" onclick="descargarImagen()">📷 Descargar Imagen (PNG)</button>
    <button class="btn-descarga btn-pdf" onclick="descargarPDF()">📄 Descargar PDF</button>
    <button class="btn-descarga btn-excel" onclick="descargarExcel()">📊 Descargar Excel</button>
  </div>

  <!-- AREA A IMPRIMIR / DESCARGAR -->
  <div id="contenedor-programa">
    <div class="header-banner">
      <h1>Programa de Audio, Video y Salas</h1>
      <p>Congregación El Gallito | Agosto y Septiembre 2026</p>
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
          <tr>
            <td>02/08/2026</td>
            <td>Domingo</td>
            <td>José Pereira</td>
            <td>José Alberto González</td>
            <td>David Herrera</td>
            <td>Rodney Alfaro</td>
          </tr>
          <tr>
            <td>05/08/2026</td>
            <td>Miércoles</td>
            <td>Carlos Josué Pereira</td>
            <td>Julio Sánchez</td>
            <td>Iván Zamora</td>
            <td>Josué López</td>
          </tr>
          <tr>
            <td>09/08/2026</td>
            <td>Domingo</td>
            <td>Javier García</td>
            <td>Dashler Sánchez</td>
            <td>Kenneth Solís</td>
            <td>Walter Sánchez</td>
          </tr>
          <tr>
            <td>12/08/2026</td>
            <td>Miércoles</td>
            <td class="no-hay-reunion">--- NO HAY REUNIÓN ---</td>
            <td class="no-hay-reunion">--- NO HAY REUNIÓN ---</td>
            <td class="no-hay-reunion">--- NO HAY REUNIÓN ---</td>
            <td class="no-hay-reunion">--- NO HAY REUNIÓN ---</td>
          </tr>
          <tr>
            <td>16/08/2026</td>
            <td>Domingo</td>
            <td class="no-hay-reunion">--- NO HAY REUNIÓN ---</td>
            <td class="no-hay-reunion">--- NO HAY REUNIÓN ---</td>
            <td class="no-hay-reunion">--- NO HAY REUNIÓN ---</td>
            <td class="no-hay-reunion">--- NO HAY REUNIÓN ---</td>
          </tr>
          <tr>
            <td>18/08/2026</td>
            <td>Martes</td>
            <td>Sebastián Montero</td>
            <td>Josué López</td>
            <td>Carlos Blanco</td>
            <td>Elixander Alvarado</td>
          </tr>
          <tr>
            <td>23/08/2026</td>
            <td>Domingo</td>
            <td>Geremy Fernández</td>
            <td>José Alberto González</td>
            <td>Rafael Segura</td>
            <td>Roger Loaiza</td>
          </tr>
          <tr>
            <td>26/08/2026</td>
            <td>Miércoles</td>
            <td>David Herrera</td>
            <td>Sebastián Montero</td>
            <td>Rafael Segura</td>
            <td>Carlos Enrique Pereira</td>
          </tr>
          <tr>
            <td>30/08/2026</td>
            <td>Domingo</td>
            <td>Dashler Sánchez</td>
            <td>Carlos Josué Pereira</td>
            <td>Walter Sánchez</td>
            <td>Elixander Alvarado</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- LÓGICA JAVASCRIPT DE DESCARGA -->
  <script>
    // 1. DESCARGAR COMO IMAGEN (PNG ALTA RESOLUCIÓN)
    async function descargarImagen() {
      await document.fonts.ready;
      const elemento = document.getElementById('contenedor-programa');
      
      html2canvas(elemento, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff'
      }).then(canvas => {
        const enlace = document.createElement('a');
        enlace.download = 'Programa_Audio_Video_Salas.png';
        enlace.href = canvas.toDataURL('image/png');
        enlace.click();
      });
    }

    // 2. DESCARGAR COMO PDF (DENTRO DE HOJA HORIZONTAL)
    function descargarPDF() {
      const elemento = document.getElementById('contenedor-programa');
      
      const opciones = {
        margin:       0.3,
        filename:     'Programa_Audio_Video_Salas.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
      };

      html2pdf().set(opciones).from(elemento).save();
    }

    // 3. DESCARGAR COMO EXCEL (.XLSX)
    function descargarExcel() {
      const tabla = document.querySelector('#contenedor-programa table');
      
      if (!tabla) {
        alert('No se encontró ninguna tabla para exportar');
        return;
      }

      // Genera el libro respetando los acentos y la ñ
      const libro = XLSX.utils.table_to_book(tabla, { sheet: "Programa" });
      XLSX.writeFile(libro, 'Programa_Audio_Video_Salas.xlsx');
    }
  </script>
</body>
</html>
