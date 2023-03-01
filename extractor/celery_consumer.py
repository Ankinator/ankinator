from celery import Celery

from extractor.pdf_extractor import extract_text_from_pdf

app = Celery('extractor')
app.conf.task_default_queue = "extractor"
app.conf.task_default_routing_key = "extract.task"
app.conf.accept_content = ["json", "pickle"]


@app.task(name="extract_text_from_pdf")
def task_extract_text_from_pdf(pdf_file):
    pages = extract_text_from_pdf(pdf_file)
    print(pages)
