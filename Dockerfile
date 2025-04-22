FROM ubuntu:latest
SHELL ["/bin/bash", "-c"]

RUN mkdir /app
COPY requirements.txt /app

RUN apt-get update -y
RUN apt-get install -y python3 python3-pip python3-venv postgresql libpq-dev libgdal-dev libgl1
RUN python3 -m venv /app/venv
RUN source /app/venv/bin/activate
RUN python3 -m pip install --break-system-packages -r /app/requirements.txt

WORKDIR /app
