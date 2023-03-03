from fastapi import FastAPI, UploadFile
from celery import Celery

celery_app = Celery('api')

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/uploadpdf")
async def upload_pdf_file(file: UploadFile):
    celery_app.send_task("extract_text_from_pdf", queue="extractor", routing_key="extract.pdf",
                         kwargs={"pdf_file": file.file}, serializer="pickle")
    return {"filename": file.filename}
