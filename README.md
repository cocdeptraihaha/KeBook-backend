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
- **API Docs (Markdown)**: `docs/API_DOCS.md` – tài liệu chi tiết các route  

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

### Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

Backend chỉ verify token hợp lệ rồi trả về message.  
Vì dùng JWT stateless, **logout thực tế là xoá token ở phía client** (localStorage/cookie…).

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

## 4.1 API modules chính (v1)

- **Auth**: `/api/v1/auth/*` (register, verify-otp, login, forgot/reset password)
- **Users**: `/api/v1/users/*` (me, admin user management, points adjust)
- **Books / Categories / Cart**: `/api/v1/books/*`, `/api/v1/categories/*`, `/api/v1/cart/*`
- **Orders**: `/api/v1/orders/*` (checkout, my orders, admin orders, status)
- **Promotions**: `/api/v1/promotions/*` (create/list/update, issue user, stats)
- **Points / Rewards**: `/api/v1/points/*` (admin reward CRUD, user redeem)
- **Return Requests**: `/api/v1/return-requests/*` (user create/list, admin process)
- **Notifications / Support**: `/api/v1/notifications/*`, `/api/v1/support-requests/*`

---

## 4.2 Postman test kit

Repo đã có sẵn bộ Postman để test API:

- Collection: `postman/Backend_Kebook_API.postman_collection.json`
- Environment local: `postman/Backend_Kebook_Local.postman_environment.json`

### Cách chạy nhanh

1. Import cả **collection** và **environment** vào Postman.
2. Chọn environment `KeBook Local`.
3. Chạy theo thứ tự:
   - `Auth / Login User`
   - `Auth / Login Admin`
4. Collection tự lưu token vào biến:
   - `user_token`
   - `admin_token`
5. Với các API phụ thuộc dữ liệu (`order_id`, `order_item_id`, `promotion_id`), cập nhật biến theo dữ liệu thực tế DB.

### Nhóm request đã có trong collection

- Auth, Users Admin
- Promotions
- Point Rewards
- Orders
- Return Requests (create/list/process)

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
│   ├── dependencies.py      # Auth, get_current_user, get_current_superuser
│   └── v1/
│       ├── router.py        # Gộp routes v1
│       └── endpoints/
│           ├── auth.py      # Register/Login + OTP activation/reset password
│           ├── users.py     # CRUD users (cần JWT)
│           ├── books.py     # Sách (public + admin)
│           ├── categories.py
│           ├── cart.py        # Giỏ hàng
│           ├── orders.py      # Đơn hàng, checkout
│           ├── reviews.py     # Đánh giá sách
│           ├── promotions.py
│           ├── points.py      # Điểm tích lũy, rewards
│           ├── return_requests.py
│           ├── notifications.py
│           ├── support_requests.py
│           ├── admin_dashboard.py
│           └── test_utils.py # Test-only (OTP, make-admin)
├── core/
│   ├── config.py            # Settings từ .env
│   ├── database.py          # Async SQLAlchemy, get_db
│   └── security.py          # JWT, hash password
├── models/
│   ├── otp.py                # Model OTP
│   ├── user.py               # Model User
│   ├── order.py              # Model Order
│   ├── promotion.py          # Model Promotion
│   └── return_request.py     # Model ReturnRequest
├── schemas/
│   ├── user.py               # Pydantic schemas user/auth
│   ├── order.py
│   ├── promotion.py
│   └── return_request.py
├── repositories/            # Data access
│   ├── base_repository.py
│   ├── user_repository.py
│   ├── order_repository.py
│   ├── promotion_repository.py
│   └── return_request_repository.py
├── services/                # Business logic
│   ├── email_service.py
│   ├── otp_service.py
│   ├── user_service.py
│   ├── order_service.py
│   ├── promotion_service.py
│   ├── points_service.py
│   └── return_request_service.py
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

Nếu cần thêm endpoint hoặc đổi cấu trúc, có thể mở rộng theo pattern hiện tại (endpoint → schema → service → repository).
