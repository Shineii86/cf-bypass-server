FROM python:3.11-slim
WORKDIR /app
COPY server.py .
EXPOSE 8000
CMD ["python", "server.py"]
