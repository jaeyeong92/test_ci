FROM python:3.12.3-slim

COPY . /app

RUN pip install flask

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "run.py"]
