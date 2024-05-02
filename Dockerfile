FROM python:3.12.3

COPY . /app

RUN pip install flask

WORKDIR /app

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80
ENV FLASK_ENV=production

EXPOSE 80

ENTRYPOINT ["flask", "run"]
