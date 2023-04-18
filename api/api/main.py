from fastapi import File, UploadFile, Depends, FastAPI, HTTPException, status
from celery import Celery
from datetime import timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm

from api.user_authentication import Token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token, get_current_active_user
from api.user_database import User, create_model_result_placeholder_for_user, get_user

celery_app = Celery('api')

app = FastAPI(title="Ankinator", description="Ankinator API", version="0.1", max_request_size=52428800)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/uploadpdf")
async def upload_pdf_file(file: UploadFile, current_user: Annotated[User, Depends(get_current_active_user)]):
    pdf_content = await file.read()
    document_id = create_model_result_placeholder_for_user(current_user.username)
    document = {
        "document_id": document_id,
        "pdf_file": pdf_content
    }
    celery_app.send_task("extract_text_from_pdf", queue="extractor", routing_key="extract.task",
                         kwargs={"document": document}, serializer="pickle")
    return {"document_id": document_id}


@app.get("/result")
async def root(document_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    db_user = get_user(current_user.username)
    if db_user.model_results[document_id] is None:
        return {"model_result": "PENDING"}
    else:
        return {"model_result": db_user.model_results[document_id]}


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


@app.get("/users/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
