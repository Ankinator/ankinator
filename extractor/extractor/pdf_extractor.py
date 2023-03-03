from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_file) -> [(int, str)]:
    reader = PdfReader(pdf_file)
    pages = []
    for page_index, page_content in enumerate(reader.pages, 1):
        pages.append((page_index, page_content.extract_text()))
    return pages
