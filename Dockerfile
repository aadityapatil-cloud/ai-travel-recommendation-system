# Pin the exact Python version ourselves — this bypasses whatever Render's
# native "Python 3" environment has been auto-selecting (which kept using 3.14
# regardless of runtime.txt / PYTHON_VERSION).
FROM python:3.11-slim

WORKDIR /app

# Install system build tools needed by some packages (harmless if unused)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
