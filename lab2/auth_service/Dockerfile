FROM python:3.12-alpine
WORKDIR /src
COPY . .
RUN pip install -r src/requirements.txt
CMD ["python", "src/app/main.py"]
EXPOSE 8000