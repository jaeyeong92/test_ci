FROM python:3.12.3

COPY . /app

RUN pip install flask

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 80

ENTRYPOINT ["flask", "run"]
