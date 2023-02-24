FROM python:3.10.10-slim-buster
COPY ./extractor/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY /extractor /extractor
WORKDIR /extractor
CMD [ "python", "extractor/main.py"]