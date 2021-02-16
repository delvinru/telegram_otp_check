FROM python:latest

ENV TZ Europe/Moscow

WORKDIR /bot
VOLUME [ "/bot/db" ]
VOLUME [ "/bot/logs/" ]

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["python3", "bot.py"]