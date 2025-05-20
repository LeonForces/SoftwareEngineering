FROM python:3.12-alpine
COPY . .
RUN mkdir -p /tmp/prometheus && chmod 777 /tmp/prometheus
ENV PYTHONPATH="/src/"
WORKDIR /src
RUN pip install -r requirements.txt
CMD ["python", "app/main.py"]
EXPOSE 8000