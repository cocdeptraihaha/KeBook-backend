# API Documentation – KeBook Backend

Base URL: `http://localhost:8000/api/v1`

**Auth:** Gửi JWT trong header: `Authorization: Bearer <access_token>`

**Phân quyền:**
- **Public**: Không cần auth
- **User**: Cần đăng nhập (`get_current_active_user`)
- **Admin**: Cần `is_superuser` (`get_current_superuser`)

---

## 1. Auth (`/auth`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| POST | `/register` | Public | Đăng ký user, gửi OTP qua email |
| POST | `/verify-otp` | Public | Kích hoạt tài khoản bằng OTP |
| POST | `/resend-otp` | Public | Gửi lại OTP kích hoạt (user chưa active) |
| POST | `/login` | Public | Đăng nhập, trả JWT |
| POST | `/forgot-password` | Public | Gửi OTP reset mật khẩu |
| POST | `/reset-password` | Public | Đổi mật khẩu bằng OTP |

### POST `/auth/register`
```json
// Request
{
  "email": "user@example.com",
  "username": "user123",
  "password": "matkhau123",
  "full_name": "Tên người dùng"
}

// Response 201
{
  "message": "Đăng ký thành công! Vui lòng kiểm tra email để lấy mã OTP kích hoạt tài khoản.",
  "email": "user@example.com"
}
```

### POST `/auth/verify-otp`
```json
// Request
{
  "email": "user@example.com",
  "otp_code": "123456"
}

// Response 200
{
  "access_token": "...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", ... }
}
```

### POST `/auth/resend-otp`
```json
// Request
{ "email": "user@example.com" }

// Response 200 (khi gửi thành công)
{
  "message": "Đã gửi mã OTP mới. Vui lòng kiểm tra email để kích hoạt tài khoản."
}

// Response 200 (khi email không tồn tại hoặc đã kích hoạt - bảo mật)
{
  "message": "Nếu email tồn tại và chưa kích hoạt, chúng tôi đã gửi mã OTP mới đến email của bạn."
}
```

### POST `/auth/login`
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=matkhau123
```
Response: `{ "access_token": "...", "token_type": "bearer", "user": {...} }`

### POST `/auth/forgot-password`
```json
{ "email": "user@example.com" }
```

### POST `/auth/reset-password`
```json
{
  "email": "user@example.com",
  "otp_code": "123456",
  "new_password": "matkhau_moi_123"
}
```

---

## 2. Users (`/users`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/me` | User | Thông tin user đăng nhập |
| GET | `/{user_id}` | User | Chi tiết user theo ID |
| PATCH | `/{user_id}` | User | Cập nhật (chỉ chính mình) |
| DELETE | `/{user_id}` | User | Xóa (chỉ chính mình) |

---

## 3. Books (`/books`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/` | Public | Danh sách sách |
| GET | `/{book_id}` | Public | Chi tiết sách |
| POST | `/` | Admin | Tạo sách |
| PATCH | `/{book_id}` | Admin | Cập nhật sách |

### GET `/books/` (phân trang)
Query: `?page=1&size=50&q=keyword`
- `page`: số trang (mặc định 1)
- `size`: số item mỗi trang (mặc định 50)
- `q`: tìm theo title, author

Response:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 50,
  "pages": 2
}
```

### POST `/books/` (Admin)
```json
// Request
{
  "title": "Tên sách",
  "author": "Tác giả",
  "selling_price": 100000,
  "stock_quantity": 10,
  "code": "ISBN123",
  "edition": 1,
  "publication_date": "2024-01-01",
  "book_detail_id": null
}
```

---

## 4. Categories (`/categories`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/` | Public | Danh sách danh mục |
| GET | `/roots` | Public | Danh mục gốc |
| GET | `/{category_id}` | Public | Chi tiết danh mục |
| POST | `/` | Admin | Tạo danh mục |
| PATCH | `/{category_id}` | Admin | Cập nhật danh mục |

### POST `/categories/` (Admin)
```json
{ "name": "Sách văn học", "parent_id": null }
```

---

## 5. Cart (`/cart`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/` | User | Giỏ hàng của user |
| POST | `/` | User | Thêm sách vào giỏ |
| PATCH | `/{cart_id}` | User | Cập nhật số lượng |
| DELETE | `/{cart_id}` | User | Xóa item khỏi giỏ |

### POST `/cart/`
```json
{
  "book_id": 1,
  "quantity": 2
}
```

### PATCH `/cart/{cart_id}`
```json
{ "quantity": 3 }
```

---

## 6. Orders (`/orders`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/` | User | Đơn hàng của user |
| GET | `/{order_id}` | User | Chi tiết đơn (chỉ của mình) |
| POST | `/checkout` | User | Checkout từ giỏ hàng |
| POST | `/` | User | Tạo đơn thủ công (gửi items) |
| PATCH | `/{order_id}/status` | Admin | Cập nhật trạng thái đơn |

### POST `/orders/checkout`
```json
{
  "phone_number": "0901234567",
  "shipping_address": "123 Đường ABC",
  "note": "Giao giờ hành chính",
  "promotion_code": "SALE10"
}
```

### POST `/orders/` (tạo đơn thủ công)
```json
{
  "phone_number": "0901234567",
  "shipping_address": "123 Đường ABC",
  "note": null,
  "items": [
    { "book_id": 1, "quantity": 2, "price": 50000 },
    { "book_id": 2, "quantity": 1, "price": 80000 }
  ]
}
```

### PATCH `/orders/{order_id}/status` (Admin)
```json
{ "status": "CONFIRMED" }
```
Trạng thái: `PENDING`, `CONFIRMED`, `INPROGRESS`, `SHIPPED`, `DELIVERED`, `COMPLETED`, `CANCELLED`, `RETURNED`

---

## 7. Reviews (`/reviews`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/book/{book_id}` | Public | Đánh giá theo sách |
| GET | `/book/{book_id}/avg` | Public | Điểm trung bình sách |
| POST | `/` | User | Tạo đánh giá |
| PATCH | `/{review_id}` | User | Cập nhật (chỉ của mình) |
| DELETE | `/{review_id}` | User | Xóa (chỉ của mình) |

### POST `/reviews/`
```json
{
  "book_id": 1,
  "content": "Sách hay!",
  "rate": 5
}
```
`rate`: 1–5

---

## 8. Promotions (`/promotions`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/validate` | Public | Kiểm tra mã khuyến mãi |
| GET | `/` | Admin | Danh sách mã khuyến mãi |
| POST | `/` | Admin | Tạo mã khuyến mãi |
| PATCH | `/{promo_id}` | Admin | Cập nhật mã khuyến mãi |

### GET `/promotions/validate`
Query: `?code=SALE10&order_total=100000`

Response:
```json
{
  "valid": true,
  "promotion_id": 1,
  "discount_amount": 10000,
  "name": "Giảm 10%"
}
```

### POST `/promotions/` (Admin)
```json
{
  "code": "SALE10",
  "name": "Giảm 10%",
  "discount_percent": 10,
  "max_discount": 50000,
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-12-31T23:59:59"
}
```

---

## 9. Return Requests (`/return-requests`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/` | User | Yêu cầu trả hàng của user |
| POST | `/` | User | Tạo yêu cầu trả hàng |
| PATCH | `/{req_id}/process` | Admin | Duyệt/từ chối yêu cầu |

### POST `/return-requests/`
```json
{
  "order_id": 1,
  "order_item_id": 1,
  "quantity": 1,
  "reason": "Sản phẩm lỗi"
}
```

### PATCH `/return-requests/{req_id}/process` (Admin)
```json
{ "status": "APPROVED" }
```
`status`: `APPROVED`, `REJECTED`

---

## 10. Notifications (`/notifications`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/me` | User | Thông báo của user |
| POST | `/{notification_id}/read` | User | Đánh dấu đã đọc |
| GET | `/` | Admin | Danh sách thông báo |
| POST | `/` | Admin | Tạo và gửi thông báo |

### POST `/notifications/` (Admin)
```json
{
  "user_ids": [1, 2, 3],
  "title": "Thông báo đơn hàng",
  "message": "Đơn hàng đã được xác nhận",
  "type": "INFO"
}
```

---

## 11. Support Requests (`/support-requests`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| POST | `/` | User | Gửi yêu cầu hỗ trợ |
| GET | `/` | Admin | Danh sách yêu cầu hỗ trợ |
| PATCH | `/{req_id}` | Admin | Phản hồi yêu cầu |

### POST `/support-requests/`
```json
{
  "email": "user@example.com",
  "issue": "Vấn đề",
  "description": "Mô tả chi tiết",
  "type": "ORDER"
}
```

### PATCH `/support-requests/{req_id}` (Admin)
```json
{
  "staff_response": "Đã xử lý",
  "status": "RESOLVED"
}
```

---

## 12. Payments (`/payments`)

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| POST | `/sepay/create` | User | Tạo thanh toán SePay |
| GET | `/sepay/success` | Public | Callback redirect khi thành công |
| GET | `/sepay/error` | Public | Callback redirect khi lỗi |
| GET | `/sepay/cancel` | Public | Callback redirect khi hủy |
| POST | `/sepay/ipn` | Public | IPN – SePay gửi POST khi có giao dịch |

### POST `/payments/sepay/create`
Query: `?order_id=1&success_url=...&error_url=...&cancel_url=...&payment_method=CARD`

Response:
```json
{
  "checkout_url": "https://pay-sandbox.sepay.vn/v1/checkout/init",
  "form_data": {
    "amount": "150000",
    "order_invoice_number": "INV_1_20240225120000",
    "order_description": "Thanh toan don hang #1",
    ...
  },
  "order_invoice_number": "INV_1_20240225120000"
}
```
Client POST form_data đến checkout_url để chuyển hướng user sang SePay.

### POST `/payments/sepay/ipn`
SePay gửi POST JSON khi có giao dịch. Header: `X-Secret-Key` (nếu cấu hình). Cần trả về HTTP 200 để xác nhận đã nhận.

---

## 13. Test Utils (`/test`) – Chỉ khi TESTING=1 hoặc test.db

| Method | Path | Auth | Mô tả |
|--------|------|------|------|
| GET | `/otp` | Public | Lấy OTP theo email (cho test) |
| POST | `/make-admin` | Public | Set is_superuser cho user |

---

## Health Check

| Method | Path | Mô tả |
|--------|------|------|
| GET | `/` | `{"message": "Backend Kebook API", "docs": "/docs"}` |
| GET | `/kaithhealthcheck` | `{"status": "ok"}` |

---

## Mã lỗi thường gặp

| Code | Mô tả |
|------|-------|
| 400 | Bad Request – dữ liệu không hợp lệ |
| 401 | Unauthorized – chưa đăng nhập hoặc token hết hạn |
| 403 | Forbidden – không có quyền |
| 404 | Not Found – không tìm thấy tài nguyên |
