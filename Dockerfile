FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["uvicorn", "app.main:yac","--port", "8080", "--reload"]
