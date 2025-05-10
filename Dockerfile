FROM python:3.9-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY config.py .

CMD [ "python", "./main.py" ]