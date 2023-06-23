FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/backend
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN ["chmod", "+x", "/usr/src/backend/entrypoint.sh"]
ENTRYPOINT [ "/usr/src/backend/entrypoint.sh" ]