FROM python:3.12-alpine
COPY . .
ENV PYTHONPATH="/src/"
RUN mkdir -p /tmp/prometheus && chmod 777 /tmp/prometheus
WORKDIR /src
RUN apk update && apk add --no-cache \
    librdkafka-dev \
    build-base \
    python3-dev \
    curl
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app/main.py"]
EXPOSE 8000