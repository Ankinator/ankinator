import io

from fastapi import UploadFile, Depends, FastAPI, HTTPException, status, Body, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from celery import Celery
from datetime import timedelta
from typing import Annotated, List
import base64
from pypdfium2 import PdfDocument

from api.anki_export import create_anki_export
from api.pdf_document_database import save_pdf_file, load_pdf_file, get_all_documents_for_user
from api.user_authentication import Token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token, get_current_active_user, create_session_user
from api.extractor_database import load_processed_pdf_document
from api.user_database import User, create_model_result_placeholder_for_user, get_user, update_user_result

celery_app = Celery('api')

app = FastAPI(title="Ankinator", description="Ankinator API", version="0.1", max_request_size=52428800)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/uploadpdf")
async def upload_pdf_document(file: UploadFile, current_user: Annotated[User, Depends(get_current_active_user)]):
    pdf_file = await file.read()
    pdf_save_status = save_pdf_file(pdf_file, file.filename, current_user.username)
    return pdf_save_status


@app.post("/generation/extraction/classifier/start")
async def start_extraction_classifier(current_user: Annotated[User, Depends(get_current_active_user)],
                                      pdf_document_id: str):
    result_id = create_model_result_placeholder_for_user(current_user.username, pdf_document_id)
    pdf_file, _ = load_pdf_file(pdf_document_id)
    document = {
        "pdf_document_id": pdf_document_id,
        "result_id": result_id,
        "pdf_file": pdf_file
    }
    celery_app.send_task("classify_pdf_document_page_relevance", queue="extractor", routing_key="extract.task",
                         kwargs={"document": document}, serializer="pickle")

    return {"result_id": result_id}


@app.post("/generation/questions/start")
async def start_flashcard_generation(current_user: Annotated[User, Depends(get_current_active_user)],
                                     pdf_document_id: str = Body(...),
                                     result_id: str = Body(None), pages: List[str] = Body(None),
                                     model: str = Body(None), domain: str = Body(None),
                                     ):
    if pages is not None and (len(pages) == 1):  # Required for swagger
        pages = [item.strip() for item in pages[0].split(",")]

    if pages is not None and len(pages) > 0:
        pages = [int(i) for i in pages]

    pdf_file, _ = load_pdf_file(pdf_document_id)

    if result_id is None:
        result_id = create_model_result_placeholder_for_user(current_user.username, pdf_document_id)
        if pages is None:
            pages = list(range(1, len(PdfDocument(pdf_file)) + 1))
        update_user_result(result_id, pages=pages, model_result="PENDING")
    else:
        if pages is None:
            pages = get_user(current_user.username).model_results[result_id]["pages"]
            update_user_result(result_id, model_result="PENDING")
        else:
            update_user_result(result_id, pages=pages, model_result="PENDING")

    document = {
        "pdf_document_id": pdf_document_id,
        "result_id": result_id,
        "pdf_file": pdf_file,
        "pages": pages,
        "model": model,
        "domain": domain
    }
    celery_app.send_task("extract_text_from_pdf", queue="extractor", routing_key="extract.task",
                         kwargs={"document": document}, serializer="pickle")
    return {"result_id": result_id}


@app.get("/generation/result")
async def get_flashcard_results(result_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    db_user = get_user(current_user.username)
    if db_user.model_results[result_id] is None:
        return {"model_result": "PENDING"}
    else:
        return db_user.model_results[result_id]


@app.get("/generation/result/pdf")
async def get_flashcard_result_pdf(result_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    db_user = get_user(current_user.username)
    if db_user.model_results[result_id] is None:
        return {"model_result": "PENDING"}
    else:
        if db_user.model_results[result_id]["model_result"] is None or \
                db_user.model_results[result_id]["model_result"] == "PENDING":
            return {"model_result": "PENDING"}
        pdf_document = load_processed_pdf_document(result_id)

        pdf_blob = pdf_document.output(dest='S')
        pdf_base64 = base64.b64encode(pdf_blob).decode('utf-8')

        response = Response(content=pdf_base64, media_type="application/pdf")
        response.headers["Content-Disposition"] = f"inline; filename=result_document_{result_id}.pdf"
        return response


@app.get("/pdf")
async def get_pdf_document(pdf_document_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    pdf_file, pdf_document_name = load_pdf_file(pdf_document_id)
    pdf_document = PdfDocument(pdf_file)

    pdf_bytes = io.BytesIO()
    pdf_document.save(pdf_bytes)
    pdf_bytes.seek(0)

    pdf_base64 = base64.b64encode(pdf_bytes.read()).decode('utf-8')

    response = Response(content=pdf_base64, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"inline; {pdf_document_name}"
    return response


@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/session", response_model=Token)
async def random_user_session():
    access_token = create_session_user()
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    db_user = get_user(current_user.username)
    all_pdf_documents = get_all_documents_for_user(current_user.username)
    results_to_remove = []
    for result_id in db_user.model_results:
        pdf_document_name = next((pdf["pdf_document_name"] for pdf in all_pdf_documents if
                                  pdf["pdf_document_id"] == db_user.model_results[result_id]["pdf_document_id"]), None)
        db_user.model_results[result_id]["pdf_document_name"] = pdf_document_name

        if db_user.model_results[result_id]["model_result"] is None or \
                db_user.model_results[result_id]["model_result"] == "PENDING":
            results_to_remove.append(result_id)
    for result_id in results_to_remove:
        db_user.model_results.pop(result_id)
    return db_user


@app.post("/create_flashcards")
async def create_flashcards_for_pdf(current_user: Annotated[User, Depends(get_current_active_user)],
                                    result_id: str = Body(...), questions: List[str] = Body(...)):
    anki_export = create_anki_export(current_user.username, result_id, questions)

    response = Response(content=anki_export, media_type="application/octet-stream")
    response.headers["Content-Disposition"] = f"attachment; filename=deck_{result_id}.apkg"
    return response


@app.get("/users/me/pdfs")
async def read_user_pdf_documents(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return get_all_documents_for_user(current_user.username)
