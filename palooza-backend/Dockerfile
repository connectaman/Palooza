FROM python:3.10-slim-bullseye

WORKDIR /code

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc libsndfile1 git curl unzip libgl1-mesa-glx libglib2.0-0

RUN apt-get install -y git python3-dev

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

COPY ./ /code/

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "600", "main:app", "-k", "uvicorn.workers.UvicornWorker"]
