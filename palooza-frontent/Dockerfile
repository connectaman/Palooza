FROM node:22-alpine
WORKDIR /app

COPY package.json ./
COPY package-lock.json ./

RUN npm ci

COPY . ./

ARG BACKEND_API_URL
ENV REACT_APP_BACKEND_API_URL=$BACKEND_API_URL

RUN npm run build

EXPOSE 3000

ENTRYPOINT ["npm", "start"]