FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install flask --no-cache-dir

EXPOSE 5000

ENV AZ="ap-south-1a"
ENV APP_VERSION="v1.0.0"
 
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["python", "app.py"]
