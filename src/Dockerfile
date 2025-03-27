FROM python:3.10

WORKDIR /app

COPY ../requirements.txt .

RUN pip install -r requirements.txt

COPY ../migrations ./migrations
COPY ../src ./src
COPY ../.env .
COPY ../alembic.ini .

ENV PYTHONPATH=/app
