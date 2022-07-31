FROM node:16.16.0-alpine3.16

ENV REACT_APP_BASE_URL=ws://localhost:8000/quiz

WORKDIR /code/site
COPY package.json package-lock.json .dockerignore  /code/site/
COPY . /code/site

RUN npm install --quiet
