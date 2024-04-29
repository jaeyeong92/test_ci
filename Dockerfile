FROM python:3.12.3

COPY . /

RUN pip install flask

WORKDIR /

RUN apt-get update && apt-get install -y pkg-config
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
