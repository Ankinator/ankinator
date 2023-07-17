from fastapi import UploadFile, Depends, FastAPI, HTTPException, status, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from celery import Celery
from datetime import timedelta
from typing import Annotated, List

from fastapi.security import OAuth2PasswordRequestForm

from api.user_authentication import Token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token, get_current_active_user, create_session_user
from api.user_database import User, create_model_result_placeholder_for_user, get_user
from api.extractor_database import load_processed_pdf_document

import base64

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
async def upload_pdf_file(file: UploadFile, current_user: Annotated[User, Depends(get_current_active_user)],
                          pages: List[str] = Body(None), model: str = Body(None), domain: str = Body(None)):
    pdf_content = await file.read()
    document_id = create_model_result_placeholder_for_user(current_user.username)

    if pages is not None and (len(pages) == 1):  # Required for swagger
        pages = [item.strip() for item in pages[0].split(",")]

    if pages is not None and len(pages) > 0:
        pages = [int(i) for i in pages]

    document = {
        "document_id": document_id,
        "pdf_file": pdf_content,
        "pages": pages,
        "model": model,
        "domain": domain
    }
    celery_app.send_task("extract_text_from_pdf", queue="extractor", routing_key="extract.task",
                         kwargs={"document": document}, serializer="pickle")
    return {"document_id": document_id}


@app.get("/result")
async def get_flashcard_results(document_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    db_user = get_user(current_user.username)
    if db_user.model_results[document_id] is None:
        return {"model_result": "PENDING"}
    else:
        return db_user.model_results[document_id]


@app.get("/resultpdf")
async def get_flashcard_result_document(document_id: str,
                                        current_user: Annotated[User, Depends(get_current_active_user)]):
    db_user = get_user(current_user.username)
    if db_user.model_results[document_id] is None:
        return {"model_result": "PENDING"}
    else:
        pdf_document = load_processed_pdf_document(document_id)

        pdf_blob = pdf_document.output(dest='S')
        pdf_base64 = base64.b64encode(pdf_blob).decode('utf-8')

        response = Response(content=pdf_base64, media_type="application/pdf")
        response.headers["Content-Disposition"] = f"inline; filename=result_document_{document_id}.pdf"
        return response


@app.post("/login", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
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
    return current_user
