FROM python:3.10.10-slim-buster

RUN apt-get update && apt-get upgrade -y && apt-get install tesseract-ocr -y && apt-get install tesseract-ocr-deu -y

COPY ./extractor/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY /extractor /extractor
WORKDIR /extractor

RUN adduser --system --no-create-home ankinator
USER ankinator

CMD [ "python", "-m", "celery", "--app", "celery_consumer", "worker", "--loglevel=INFO"]