FROM node:18-alpine3.15 as builder

RUN npm -g install pnpm

RUN mkdir -p /usr/src/frontend
WORKDIR /usr/src/frontend

COPY ./frontend .

RUN pnpm config set registry https://registry.npmmirror.com/ \
  && pnpm install \
  && pnpm run build

FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/backend
COPY ./backend .
COPY --from=builder /usr/src/frontend/dist /usr/src/backend/dist

RUN pip install -r requirements.txt

RUN ["chmod", "+x", "/usr/src/backend/entrypoint.sh"]
ENTRYPOINT [ "/usr/src/backend/entrypoint.sh" ]