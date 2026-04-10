FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend /app/backend
COPY frontend /app/frontend
COPY main.py /app/main.py

EXPOSE 8000

CMD ["python3", "main.py"]
