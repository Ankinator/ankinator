from fastapi import FastAPI, File, UploadFile
from celery import Celery

celery_app = Celery('api')

app = FastAPI(title="Ankinator", description="Ankinator API", version="0.1", max_request_size=52428800)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/uploadpdf")
async def upload_pdf_file(file: UploadFile = File(...)):
    contents = await file.read()
    celery_app.send_task("extract_text_from_pdf", queue="extractor", routing_key="extract.pdf",
                         kwargs={"pdf_file": contents}, serializer="pickle")
    return {"filename": file.filename}
