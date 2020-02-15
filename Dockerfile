FROM python:3.7-slim-stretch

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache -r requirements.txt

COPY . .

CMD ["python", "app.py"]