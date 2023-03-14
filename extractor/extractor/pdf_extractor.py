import pytesseract
from pypdfium2 import PdfDocument, PdfPage

NUMBER_OF_TOKENS_TO_RUN_OCR = 20
PRIMARY_EXTRACTION_BOOST = 1.2


def plain_pdf_extraction(pdf_document: PdfDocument) -> [(int, str)]:
    pages = []
    for page_index, page_content in enumerate(pdf_document, 0):
        page_text: str = page_content.get_textpage().get_text_range()
        pages.append((page_index, page_text))
    return pages


def extract_text(pdf_file, language: str = "eng"):
    pdf_document = PdfDocument(pdf_file)
    extracted_pages = plain_pdf_extraction(pdf_document)
    for page_index, page_text in extracted_pages:
        plain_extraction_text_length = len(page_text.split(" "))
        if plain_extraction_text_length < NUMBER_OF_TOKENS_TO_RUN_OCR:
            ocr_text = ocr_extraction(pdf_document.get_page(page_index), language=language)
            if len(ocr_text.split(" ")) > plain_extraction_text_length * PRIMARY_EXTRACTION_BOOST:
                extracted_pages[page_index] = (page_index, ocr_text + "OCR")
            else:
                extracted_pages[page_index] = (page_index, page_text)

    return extracted_pages


def ocr_extraction(page: PdfPage, language: str = "eng") -> str:
    bitmap = page.render(scale=2)  # sacle=2 to increase resolution
    pil_image = bitmap.to_pil()
    text = pytesseract.image_to_string(pil_image, lang=language)
    return text
