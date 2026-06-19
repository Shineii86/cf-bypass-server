FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir cloudscraper
COPY cf_bypass_server.py .
EXPOSE 8000
CMD ["python", "cf_bypass_server.py"]
