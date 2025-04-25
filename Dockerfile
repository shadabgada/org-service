FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ./scripts/wait_for_db.sh /app/scripts/wait_for_db.sh

RUN chmod +x scripts/wait_for_db.sh

#CMD ["sh", "-c", "./scripts/wait_for_db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
#CMD ["sh", "-c", "/app/scripts/wait_for_db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
#CMD ["sh", "-c", "sleep 5 && uvicorn app.main:app..."]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]