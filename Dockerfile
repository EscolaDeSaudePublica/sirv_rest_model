# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
#RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

EXPOSE 5100

COPY app.py /app
COPY config.yml /app
COPY dados.txt /app
COPY dados_vacinacao.txt /app
ADD templates /app/templates

CMD  python app.py

