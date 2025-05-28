FROM python:3.10-slim
WORKDIR /app
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
RUN mkdir -p /root/.postgresql && \
    wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" -O /root/.postgresql/root.crt
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]