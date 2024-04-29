FROM python:3.12.3-slim

COPY . /

RUN pip install flask

WORKDIR /

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
