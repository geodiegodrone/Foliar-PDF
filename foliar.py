import os  # Importa el módulo os para interactuar con el sistema operativo
import PyPDF2  # Importa PyPDF2 para manipular archivos PDF
from tkinter import Tk, simpledialog, filedialog  # Importa Tkinter para crear diálogos de entrada y selección de archivos
from reportlab.pdfgen import canvas  # Importa canvas de ReportLab para generar contenido PDF
from reportlab.lib.pagesizes import letter  # Importa el tamaño de página letter de ReportLab
from reportlab.lib.units import inch  # Importa unidades de medida de ReportLab
import io  # Importa io para manejar flujos de datos en memoria

def foliar_pdfs(start_folio, directory):
	current_folio = start_folio  # Inicializa el folio actual con el folio de inicio
	for root, _, files in os.walk(directory):  # Recorre todos los archivos en el directorio dado
		for file in sorted(files):  # Ordena y recorre cada archivo
			if file.endswith('.pdf'):  # Verifica si el archivo es un PDF
				pdf_path = os.path.join(root, file)  # Obtiene la ruta completa del archivo PDF
				current_folio = foliar_pdf(pdf_path, current_folio)  # Folia el PDF y actualiza el folio actual

def foliar_pdf(pdf_path, start_folio):
	pdf_reader = PyPDF2.PdfReader(pdf_path)  # Lee el archivo PDF
	pdf_writer = PyPDF2.PdfWriter()  # Crea un escritor de PDF

	for page_num in range(len(pdf_reader.pages)):  # Recorre todas las páginas del PDF
		page = pdf_reader.pages[page_num]  # Obtiene la página actual

		# Crear un PDF temporal con el número de folio
		packet = io.BytesIO()  # Crea un flujo de datos en memoria
		can = canvas.Canvas(packet, pagesize=letter)  # Crea un canvas para dibujar en el PDF temporal
		can.setFont("Helvetica-Bold", 10)  # Establece la fuente y el tamaño
		can.drawString(3.5 * inch, 10.8 * inch, f"{start_folio + page_num}")  # Dibuja el número de folio en el PDF temporal
		can.save()  # Guarda el canvas

		# Mover al inicio del archivo temporal
		packet.seek(0)  # Mueve el puntero al inicio del flujo de datos
		new_pdf = PyPDF2.PdfReader(packet)  # Lee el PDF temporal
		page.merge_page(new_pdf.pages[0])  # Fusiona la página temporal con la página original

		pdf_writer.add_page(page)  # Añade la página al escritor de PDF

	temp_pdf_path = pdf_path + ".temp"  # Define la ruta temporal para el PDF
	with open(temp_pdf_path, 'wb') as output_pdf:  # Abre el archivo temporal en modo escritura binaria
		pdf_writer.write(output_pdf)  # Escribe el contenido del escritor de PDF en el archivo temporal

	os.replace(temp_pdf_path, pdf_path)  # Reemplaza el archivo original con el archivo temporal

	return start_folio + len(pdf_reader.pages)  # Devuelve el nuevo folio de inicio

def main():
	root = Tk()  # Crea una instancia de Tkinter
	root.withdraw()  # Oculta la ventana principal de Tkinter

	start_folio = simpledialog.askinteger("Input", "Ingrese el número de folio inicial:")  # Pide al usuario el número de folio inicial
	directory = filedialog.askdirectory(title="Seleccione la carpeta con los PDFs")  # Pide al usuario seleccionar el directorio con los PDFs

	if start_folio is not None and directory:  # Verifica que se haya ingresado un folio y seleccionado un directorio
		foliar_pdfs(start_folio, directory)  # Llama a la función para foliar los PDFs
		print("Foliado completado.")  # Imprime un mensaje de completado

if __name__ == "__main__":
	main()  # Llama a la función principal si el script se ejecuta directamente