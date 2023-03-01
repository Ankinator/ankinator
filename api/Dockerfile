FROM python:3.10.10-slim-buster
COPY ./api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api /api
WORKDIR /api

RUN adduser --system --no-create-home ankinator
USER ankinator

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]