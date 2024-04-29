FROM python:3.12.3

COPY . /

RUN pip install flask

WORKDIR /

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80
ENV FLASK_ENV=production

EXPOSE 80

ENTRYPOINT ["flask", "run"]
