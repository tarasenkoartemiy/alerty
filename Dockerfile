FROM python:3.10-alpine3.18

WORKDIR /alerty
COPY . .
EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk update &&  \
    apk add postgresql-client build-base postgresql-dev &&  \
    pip install --upgrade pip &&  \
    pip install -r requirements.txt \