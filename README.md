# Backend Kebook – FastAPI (JWT + OTP Email)

Backend FastAPI async với **JWT auth**, **đăng ký/kích hoạt bằng OTP qua email**, và cấu trúc theo layer (**API → service → repository → model/schema**).

**Phạm vi dự án: CHỈ BACKEND – KHÔNG LÀM FRONTEND.** API có thể được gọi từ bất kỳ client nào (Swagger UI, Postman, cURL, React, Vue, mobile app…).

---

## 1. Tính năng chính

- **Auth**: đăng ký → gửi OTP → verify OTP kích hoạt → login lấy JWT  
- **Forgot password**: gửi OTP → reset password  
- **Async SQLAlchemy**: hỗ trợ MySQL (driver `aiomysql`) và có default SQLite nếu không set `.env`  
- **Background cleanup**: định kỳ dọn OTP hết hạn và user chưa kích hoạt có OTP đã hết hạn  

---

## 2. Chuẩn bị môi trường

### Tạo và kích hoạt virtual environment (venv)

**Windows (PowerShell):**
```powershell
# Đã tạo sẵn thư mục venv, chỉ cần kích hoạt:
.\venv\Scripts\Activate.ps1

# Nếu chưa có venv, tạo mới:
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Cấu hình biến môi trường

```bash
# Copy file mẫu
copy .env.example .env   # Windows (PowerShell/CMD)
cp .env.example .env    # Linux/macOS

# Chỉnh .env: DATABASE_URL, SECRET_KEY, SMTP_*, OTP_*
```

#### Các biến quan trọng trong `.env`

- **DATABASE_URL**: DSN database (ưu tiên MySQL async)
  - Ví dụ local MySQL: `mysql+aiomysql://user:password@localhost:3306/kebook`
  - Nếu không set sẽ dùng default trong code (SQLite async)
- **SECRET_KEY**: bắt buộc đổi khi chạy production
- **SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASSWORD/SMTP_FROM_EMAIL**: dùng để gửi OTP
- **OTP_EXPIRE_SECONDS / OTP_LENGTH**: cấu hình OTP

> Lưu ý: `.env.example` chỉ là file mẫu. Đừng giữ credential thật trong repo và **không commit** `.env`.

### MySQL (tuỳ chọn)

- Cài và chạy MySQL (XAMPP, MySQL Server, Docker...).
- Tạo database: `CREATE DATABASE kebook;`
- Trong `.env` đặt: `DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/kebook`

---

## 3. Chạy ứng dụng

### Chạy server (development)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: `http://localhost:8000`  
- Swagger UI: `http://localhost:8000/docs`  
- ReDoc: `http://localhost:8000/redoc`  

### Chạy không reload (production-style)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 4. Hướng dẫn sử dụng API (flow chuẩn: Register → Verify OTP → Login)

### Đăng ký user

Endpoint khuyến nghị (có gửi OTP):

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "user123",
  "password": "matkhau123",
  "full_name": "Tên người dùng"
}
```

Phản hồi sẽ yêu cầu bạn kiểm tra email để lấy OTP kích hoạt.

### Verify OTP để kích hoạt (lấy token)

```http
POST /api/v1/auth/verify-otp
Content-Type: application/json

{
  "email": "user@example.com",
  "otp_code": "123456"
}
```

### Đăng nhập (lấy token)

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=matkhau123
```

Trả về: `{"access_token": "...", "token_type": "bearer"}`

### Gọi API cần đăng nhập

Thêm header:

```http
Authorization: Bearer <access_token>
```

Ví dụ:

- `GET /api/v1/users/me` – thông tin user hiện tại  
- `GET /api/v1/users/{user_id}` – xem user theo ID  
- `PATCH /api/v1/users/{user_id}` – cập nhật (chỉ chính mình)  
- `DELETE /api/v1/users/{user_id}` – xóa (chỉ chính mình)  

---

## 5. Quên mật khẩu (OTP)

### Gửi OTP reset password

```http
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Reset password bằng OTP

```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com",
  "otp_code": "123456",
  "new_password": "matkhau_moi_123"
}
```

---

## 6. Cấu trúc dự án

```
app/
├── api/
│   ├── dependencies.py      # Auth, get_current_user
│   └── v1/
│       ├── router.py        # Gộp routes v1
│       └── endpoints/
│           ├── auth.py      # Register/Login + OTP activation/reset password
│           └── users.py     # CRUD users (cần JWT)
├── core/
│   ├── config.py            # Settings từ .env
│   ├── database.py          # Async SQLAlchemy, get_db
│   └── security.py          # JWT, hash password
├── models/
│   ├── otp.py               # Model OTP
│   └── user.py              # Model User
├── schemas/
│   └── user.py              # Pydantic schemas
├── repositories/            # Data access
│   ├── base_repository.py
│   └── user_repository.py
├── services/                # Business logic
│   ├── email_service.py
│   ├── otp_service.py
│   └── user_service.py
└── main.py                  # FastAPI app, CORS, lifespan
```

---

## 7. Chạy test

```bash
pytest
# Hoặc với asyncio
pytest -v
```

---

## 8. Công nghệ sử dụng

- **FastAPI** – Web framework  
- **SQLAlchemy 2 (async)** – ORM, session  
- **aiomysql** – Driver async cho MySQL  
- **Pydantic v2** – Validation, config  
- **pydantic-settings** – Load settings từ `.env`  
- **python-jose** – JWT  
- **bcrypt** – Hash mật khẩu  
- **uvicorn** – ASGI server  

---

## 9. Lưu ý

- Đổi `SECRET_KEY` và không commit `.env` lên git.  
- Database: nếu dùng MySQL (`aiomysql`) hãy đảm bảo MySQL đã chạy và tạo database trước (ví dụ `CREATE DATABASE kebook;`).  
- CORS đang cho phép mọi origin (`*`); production nên giới hạn domain.

Nếu cần thêm endpoint hoặc đổi cấu trúc, có thể mở rộng từ template này (thêm model, repository, service, router tương tự `users`).
