FROM python:3.7

EXPOSE 5000

WORKDIR /app

ADD ./ /app
COPY ./ /app

RUN pip install -r requirements.txt

CMD ["python", "wsgi.py", "-d", "db", "-p", "root"]