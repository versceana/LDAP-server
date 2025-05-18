FROM python:3.9-slim
WORKDIR /app
RUN mkdir -p /logs
VOLUME /logs
COPY requirements.txt ./
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt
COPY . .
ENV LOG_DIR=/logs
CMD ["python", "main.py"]