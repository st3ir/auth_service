FROM python:3.11.8-bullseye

ENV PYTHONUNBUFFERED=1                      \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir --upgrade \
    pip==23.2.1 \
    setuptools==69.1.1

WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
COPY . /usr/src/app
