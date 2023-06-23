FROM node:18-alpine3.15

WORKDIR /usr/src/frontend

RUN npm -g install pnpm
COPY package.json .
COPY pnpm-lock.yaml .

RUN pnpm config set registry https://registry.npmmirror.com/ \
  && pnpm install

COPY . .

CMD ["pnpm", "dev"]