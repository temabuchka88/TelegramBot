# syntax=docker/dockerfile:1

FROM python:alpine

WORKDIR /Bot

RUN apk add libpq-dev
RUN apk add build-base

COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools wheel
RUN pip3 install -r requirements.txt

CMD [ "python3", "bot.py"]
