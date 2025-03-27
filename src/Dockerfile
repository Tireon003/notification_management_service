FROM python:3.10

WORKDIR /app

COPY ../migrations ./migrations
COPY ../src ./src
COPY ../.env .
COPY ../alembic.ini .
COPY ../requirements.txt .

RUN pip install -r requirements.txt

ENV PYTHONPATH=/app
