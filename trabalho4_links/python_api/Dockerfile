FROM python:3.9-alpine
WORKDIR /app
RUN pip install flask redis beautifulsoup4 requests
COPY linkextractor.py .
CMD ["python", "linkextractor.py"]
