FROM node:18-alpine3.15

RUN npm -g install pnpm

RUN mkdir -p /usr/src/frontend
WORKDIR /usr/src/frontend

COPY package.json .
COPY pnpm-lock.yaml .

RUN pnpm config set registry https://registry.npmmirror.com/ \
  && pnpm install

COPY . .

CMD ["pnpm", "dev"]