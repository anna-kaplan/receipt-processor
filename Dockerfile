FROM python:3.13.2

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src /app/src

EXPOSE 5000

CMD ["python3", "/app/src/receipt_app.py"]