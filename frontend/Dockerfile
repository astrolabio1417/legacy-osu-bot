FROM node:20-alpine

WORKDIR /usr/src/frontend

COPY package.json .

RUN npm config set registry https://registry.npmmirror.com/ \
  && npm install -g pnpm vite \
  && pnpm install

COPY . .


