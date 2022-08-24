FROM python:3.7-slim

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY foodgram/ .

COPY before_loaddata.py .

COPY dump2.json .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
