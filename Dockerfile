FROM python:3.12.3

COPY . /

RUN pip install flask

WORKDIR /

RUN pip install -r requirements.txt

ENTRYPOINT ["flask", "run"]
