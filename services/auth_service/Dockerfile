FROM python:3.12-alpine
COPY . .
WORKDIR /src
RUN pip install -r requirements.txt
CMD ["python", "app/main.py"]
EXPOSE 8000