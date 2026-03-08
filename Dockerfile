# Nếu Leapcell hỗ trợ Dockerfile: copy deps trước, copy code sau → đổi code không làm mất cache pip
FROM python:3.11-slim

WORKDIR /app

# Layer 1: chỉ khi đổi requirements mới chạy lại
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: đổi code chỉ rebuild bước này
COPY . .

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
