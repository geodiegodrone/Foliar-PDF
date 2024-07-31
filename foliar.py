import os
import io
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from tkinter import Tk, simpledialog, filedialog
from reportlab.lib.units import inch

def foliar_pdf(pdf_path, start_folio):
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()
    num_pages = len(pdf_reader.pages)

    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]  # Obtiene la página actual

        packet = io.BytesIO()  # Crea un flujo de datos en memoria
        can = canvas.Canvas(packet, pagesize=letter)  # Crea un canvas para dibujar en el PDF
        can.setFont("Helvetica-Bold", 10)  # Establece la fuente y el tamaño
        can.drawString(3.5 * inch, 10.8 * inch, f"{start_folio}")  # Dibuja el número de folio en la página
        can.save()  # Guarda el contenido del canvas

        packet.seek(0)  # Reinicia el flujo de datos al principio
        new_pdf = PdfReader(packet)  # Lee el contenido del canvas como un PDF
        page.merge_page(new_pdf.pages[0])  # Fusiona el contenido del canvas con la página actual

        pdf_writer.add_page(page)  # Añade la página al escritor de PDF
        start_folio += 1  # Incrementa el folio después de procesar cada página

    temp_pdf_path = pdf_path + ".temp"  # Define una ruta temporal para el PDF
    with open(temp_pdf_path, 'wb') as output_pdf:  # Abre el archivo temporal en modo escritura binaria
        pdf_writer.write(output_pdf)  # Escribe el contenido del escritor de PDF en el archivo

    try:
        os.replace(temp_pdf_path, pdf_path)  # Reemplaza el archivo original con el archivo temporal
    except PermissionError as e:
        print(f"Error: No se pudo reemplazar el archivo {pdf_path}. {e}")
        os.remove(temp_pdf_path)  # Elimina el archivo temporal en caso de error
        raise

    return start_folio, num_pages  # Devuelve el folio actualizado y el número de páginas procesadas

def foliar_pdfs(start_folio, directory):
    pdf_files = []
    total_pages = 0

    # Recorre todas las carpetas y subcarpetas para encontrar archivos PDF
    for root, _, files in os.walk(directory):
        # Ordena las carpetas numéricamente
        subfolders = sorted([d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))],
                            key=lambda x: int(x.split('.')[0]))

        for folder in subfolders:
            folder_path = os.path.join(root, folder)
            for file in sorted(os.listdir(folder_path)):  # Ordena los archivos alfabéticamente para consistencia
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(folder_path, file))

    total_files = len(pdf_files)  # Número total de archivos PDF
    start_time = time.time()  # Tiempo de inicio del proceso

    # Procesa cada archivo PDF y actualiza el folio
    for i, pdf_path in enumerate(pdf_files):
        start_folio, num_pages = foliar_pdf(pdf_path, start_folio)
        total_pages += num_pages

        # Calcular tiempo transcurrido y estimar tiempo restante
        elapsed_time = time.time() - start_time
        avg_time_per_file = elapsed_time / (i + 1)
        remaining_files = total_files - (i + 1)
        estimated_time_remaining = avg_time_per_file * remaining_files

        # Imprimir progreso y tiempo estimado restante
        print(f"Procesado archivo {i + 1}/{total_files}. Tiempo transcurrido: {elapsed_time:.2f}s. "
              f"Tiempo estimado restante: {estimated_time_remaining:.2f}s")

    return start_folio, total_pages  # Asegura que el último folio y el total de páginas se retornen correctamente

def main():
    root = Tk()  # Crea una instancia de Tkinter
    root.withdraw()  # Oculta la ventana principal de Tkinter

    start_folio = simpledialog.askinteger("Input", "Ingrese el número de folio inicial:")  # Solicita el número de folio inicial
    directory = filedialog.askdirectory(title="Seleccione la carpeta con los PDFs")  # Solicita la carpeta con los PDFs

    if start_folio is not None and directory:  # Verifica que se haya ingresado un folio y seleccionado una carpeta
        final_folio, total_pages = foliar_pdfs(start_folio, directory)  # Llama a la función para foliar los PDFs
        print(f"Foliado completado. Último folio utilizado: {final_folio - 1}, Total de páginas procesadas: {total_pages}")  # Imprime el último folio utilizado

if __name__ == "__main__":
    main()  # Ejecuta la función principal si el script se ejecuta directamente
