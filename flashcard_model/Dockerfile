FROM python:3.10.10-slim-buster
COPY ./flashcard_model/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv
RUN pip install requests


COPY /flashcard_model /flashcard_model
WORKDIR /flashcard_model

RUN adduser --system --no-create-home ankinator
USER ankinator

CMD [ "python", "-m", "celery", "--app", "celery_consumer", "worker", "--loglevel=INFO"]