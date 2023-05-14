FROM python:3.10-alpine3.17

WORKDIR /alerty
COPY . .
EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r requirements.txt

RUN adduser --disabled-password alerty-user

USER alerty-user