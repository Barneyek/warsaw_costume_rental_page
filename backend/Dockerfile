FROM python:3.12-slim

# Ustawienia systemowe, żeby Python nie tworzył plików .pyc i wypisywał logi od razu
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalacja zależności dla Postgresa (biblioteka psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc

# Kopiowanie i instalacja wymagań
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie reszty kodu
COPY . .