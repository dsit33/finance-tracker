FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 5000

RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "flask", "--app", "app:create_app()", "run", "--host", "0.0.0.0", "--port", "5000"]