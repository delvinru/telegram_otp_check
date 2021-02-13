FROM python:latest

ENV TZ Europe/Moscow

WORKDIR /www
COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "server.py", "8080"]