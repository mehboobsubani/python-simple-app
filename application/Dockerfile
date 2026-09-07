FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py telemetry.py ollama_client.py greeting_pb2.py greeting_pb2_grpc.py ./
COPY proto ./proto

EXPOSE 5000 50051

CMD ["python", "app.py"]
