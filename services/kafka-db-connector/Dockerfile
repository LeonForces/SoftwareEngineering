FROM python:3.12-alpine

RUN apk add --no-cache \
    gcc \
    musl-dev \
    librdkafka-dev

COPY . .
ENV PYTHONPATH="/src/"
WORKDIR /src

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app/main.py"]
EXPOSE 8000