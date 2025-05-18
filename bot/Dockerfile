FROM python:3.9-slim
WORKDIR /app
RUN mkdir -p /logs
VOLUME /logs
ENV LOG_DIR=/logs
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir --default-timeout=100 \
      --trusted-host pypi.org --trusted-host files.pythonhosted.org \
      -r requirements.txt
COPY . .
CMD ["python", "main.py"]