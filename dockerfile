FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads

EXPOSE 5000

ENV ENVIRONMENT=production

ENV ADMIN_PASSWORD=admin123456

CMD ["python", "app.py"]
