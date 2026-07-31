FROM python:3.12-slim

WORKDIR /workspace

WORKDIR /workspace/app

COPY . /workspace/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
