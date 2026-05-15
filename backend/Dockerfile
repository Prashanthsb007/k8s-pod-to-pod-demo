FROM python:3.12-alpine

LABEL maintainer="Hiqode DevOps Team"
LABEL project="Vote App - Backend Pod"
LABEL version="1.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]