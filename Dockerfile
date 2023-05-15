FROM python:3.9-buster

ADD main.py .
ADD config.py .

RUN pip install pyTelegramBotAPI
RUN pip install bs4 

CMD [ "python", "./main.py" ]