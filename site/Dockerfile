FROM node:16.16
WORKDIR /code/site
COPY package.json package-lock.json /code/site/
RUN npm install --quiet

COPY . /code/site
