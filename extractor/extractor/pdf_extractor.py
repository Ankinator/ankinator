from typing import List, Tuple
from tempfile import SpooledTemporaryFile
import pytesseract
from PIL.Image import Image
from pypdfium2 import PdfDocument, PdfPage

NUMBER_OF_TOKENS_TO_RUN_OCR = 20


def plain_pdf_extraction(pdf_document: PdfDocument) -> [(int, str)]:
    pages = []
    for page_index, page_content in enumerate(pdf_document, 0):
        page_text: str = page_content.get_textpage().get_text_range()
        pages.append((page_index, page_text))
    return pages


def extract_text(pdf_file: SpooledTemporaryFile, language: str = "eng") -> List[Tuple[int, str, str, Image]]:
    pdf_document = PdfDocument(pdf_file)
    extracted_pages = plain_pdf_extraction(pdf_document)
    extracted_content: List[Tuple[int, str, str, Image]] = []
    for page_index, page_text in extracted_pages:
        plain_extraction_text_length = len(page_text.split(" "))
        page_image = pdf_page_to_image(pdf_document.get_page(page_index))
        if plain_extraction_text_length < NUMBER_OF_TOKENS_TO_RUN_OCR:
            ocr_text = ocr_extraction(page_image, language=language)
            extracted_content.append((page_index, page_text, ocr_text, page_image))
        else:
            extracted_content.append((page_index, page_text, "", page_image))
    return extracted_content


def ocr_extraction(page_image: Image, language: str = "eng") -> str:
    text = pytesseract.image_to_string(page_image, lang=language)
    return text


def pdf_page_to_image(page: PdfPage) -> Image:
    bitmap = page.render(scale=2)  # sacle=2 to increase resolution
    return bitmap.to_pil()
