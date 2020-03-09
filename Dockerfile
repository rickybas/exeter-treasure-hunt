FROM python:3.7

EXPOSE 5000

ADD / /
COPY / /

WORKDIR /

RUN pip install -r requirements.txt

CMD ["python", "app/wsgi.py", "-d", "g4yltwdo6z0izlm6.chr7pe7iynqr.eu-west-1.rds.amazonaws.com", "-u", "i95wby8x4syg4g7x","-p", "bydctjoo5fojykzv", "-n", "u105wh5j30wffa4i"]