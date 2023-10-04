FROM python:3.10-slim-bullseye

WORKDIR /code

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc libsndfile1 git curl unzip

RUN apt-get install -y git python3-dev

COPY ./requirements.txt.test /code/requirements.txt.test

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt.test

#RUN python -m spacy download en_core_web_sm

RUN export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

COPY ./ /code/

EXPOSE 8080

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "600", "main:app", "-k", "uvicorn.workers.UvicornWorker"]