FROM python:3.11.4-slim-bookworm as base

RUN apt-get update && apt-get install -y supervisor
RUN apt update && apt install -y --no-install-recommends locales; rm -rf /var/lib/apt/lists/*; sed -i '/^#.* ru_RU.UTF-8 /s/^#//' /etc/locale.gen; locale-gen

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code/

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt