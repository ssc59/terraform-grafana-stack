FROM python:3.12-slim

WORKDIR /workspace

COPY . /workspace

RUN pip install --no-cache-dir -r /workspace/app/requirements.txt

WORKDIR /workspace/app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]