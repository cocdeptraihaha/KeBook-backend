# API Documentation – KeBook Backend

Base URL: `http://localhost:8000/api/v1`

**Auth:** Send JWT in header: `Authorization: Bearer <access_token>`

**Permissions:**
- **Public**: No auth required
- **User**: Requires login (`get_current_active_user`)
- **Admin**: Requires `is_superuser` (`get_current_superuser`)

---

## Danh sách API theo nhóm chức năng

> Tất cả route dưới đây đều tồn tại trong codebase. Base: `http://localhost:8000/api/v1` (trừ Health Check ở root).

### 1. Xác thực (`/auth`)
| Method | Path | Auth |
|--------|------|------|
| POST | `/auth/register` | Public |
| POST | `/auth/verify-otp` | Public |
| POST | `/auth/resend-otp` | Public |
| POST | `/auth/login` | Public |
| POST | `/auth/forgot-password` | Public |
| POST | `/auth/reset-password` | Public |

### 2. Người dùng (`/users`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/users/me` | User |
| GET | `/users/{user_id}` | User |
| PATCH | `/users/{user_id}` | User |
| DELETE | `/users/{user_id}` | User |

### 3. Sách (`/books`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/books/` | Public |
| GET | `/books/{book_id}` | Public |
| POST | `/books/` | Admin |
| PATCH | `/books/{book_id}` | Admin |

### 4. Book Details (`/book-details`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/book-details/` | Admin |
| GET | `/book-details/{detail_id}` | Admin |
| POST | `/book-details/` | Admin |
| PATCH | `/book-details/{detail_id}` | Admin |

### 5. Danh mục (`/categories`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/categories/` | Public |
| GET | `/categories/roots` | Public |
| GET | `/categories/{category_id}` | Public |
| POST | `/categories/` | Admin |
| PATCH | `/categories/{category_id}` | Admin |

### 6. Giỏ hàng (`/cart`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/cart/` | User |
| POST | `/cart/` | User |
| PATCH | `/cart/{cart_id}` | User |
| DELETE | `/cart/{cart_id}` | User |

### 7. Đơn hàng (`/orders`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/orders/` | User |
| GET | `/orders/{order_id}` | User |
| POST | `/orders/checkout` | User |
| POST | `/orders/` | User |
| PATCH | `/orders/{order_id}/status` | Admin |

### 8. Đánh giá (`/reviews`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/reviews/book/{book_id}` | Public |
| GET | `/reviews/book/{book_id}/avg` | Public |
| POST | `/reviews/` | User |
| PATCH | `/reviews/{review_id}` | User |
| DELETE | `/reviews/{review_id}` | User |

### 9. Khuyến mãi (`/promotions`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/promotions/validate` | Public |
| GET | `/promotions/` | Admin |
| POST | `/promotions/` | Admin |
| PATCH | `/promotions/{promo_id}` | Admin |

### 10. Yêu cầu trả hàng (`/return-requests`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/return-requests/` | User |
| POST | `/return-requests/` | User |
| PATCH | `/return-requests/{req_id}/process` | Admin |

### 11. Thông báo (`/notifications`)
| Method | Path | Auth |
|--------|------|------|
| GET | `/notifications/me` | User |
| POST | `/notifications/{notification_id}/read` | User |
| GET | `/notifications/` | Admin |
| POST | `/notifications/` | Admin |

### 12. Hỗ trợ (`/support-requests`)
| Method | Path | Auth |
|--------|------|------|
| POST | `/support-requests/` | User |
| GET | `/support-requests/` | Admin |
| PATCH | `/support-requests/{req_id}` | Admin |

### 13. Test (`/test`) – Chỉ khi TESTING=1
| Method | Path | Auth |
|--------|------|------|
| GET | `/test/otp` | Public |
| POST | `/test/make-admin` | Public |
| POST | `/test/books` | Public |

### 14. Health Check (root, không thuộc /api/v1)
| Method | Path | Auth |
|--------|------|------|
| GET | `/` | Public |
| GET | `/kaithhealthcheck` | Public |
| GET | `/kaithheathcheck` | Public |

---

## 1. Auth (`/auth`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| POST | `/register` | Public | Register user, send OTP via email |
| POST | `/verify-otp` | Public | Activate account with OTP |
| POST | `/resend-otp` | Public | Resend activation OTP (inactive user only) |
| POST | `/login` | Public | Login, returns JWT |
| POST | `/forgot-password` | Public | Send OTP to reset password |
| POST | `/reset-password` | Public | Reset password with OTP |

### POST `/auth/register`
```json
// Request
{
  "email": "user@example.com",
  "username": "user123",
  "password": "password123",
  "full_name": "User Name"
}

// Response 201
{
  "message": "Registration successful. Please check your email for the OTP activation code.",
  "email": "user@example.com"
}

// Error 400
{ "detail": "Email already registered" }
{ "detail": "Username already in use" }
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
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "username": "...", "full_name": "...", "is_active": true, ... }
}

// Error 400
{ "detail": "OTP code has expired" }
{ "detail": "Invalid OTP code" }

// Error 404
{ "detail": "User not found" }
```

### POST `/auth/resend-otp`
```json
// Request
{ "email": "user@example.com" }

// Response 200 (success)
{
  "message": "New OTP sent. Please check your email to activate your account."
}

// Error 404
{ "detail": "Email not found" }
{ "detail": "Account not found" }

// Error 400
{ "detail": "Account already activated" }
```

### POST `/auth/login`
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```
(Use `username` field for email or username)

Response 200:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", ... }
}
```

Error 401: `{ "detail": "Invalid email/username or password" }`
Error 400: `{ "detail": "Account not activated. Please check your email for the OTP code." }`

### POST `/auth/forgot-password`
```json
// Request
{ "email": "user@example.com" }

// Response 200 (email exists in DB)
{
  "message": "OTP has been sent to your email."
}

// Error 404 (email not in DB)
{ "detail": "Email not found" }
```

### POST `/auth/reset-password`
```json
// Request
{
  "email": "user@example.com",
  "otp_code": "123456",
  "new_password": "newpassword123"
}

// Response 200
{
  "message": "Password changed successfully. Please log in again."
}

// Error 400
{ "detail": "OTP code has expired" }
{ "detail": "Invalid OTP code" }

// Error 404
{ "detail": "User not found" }
```

---

## 2. Users (`/users`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/me` | User | Current user info |
| GET | `/{user_id}` | User | User detail by ID |
| PATCH | `/{user_id}` | User | Update (own profile only) |
| DELETE | `/{user_id}` | User | Delete (own account only) |

---

## 3. Books (`/books`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/` | Public | List books (paginated) |
| GET | `/{book_id}` | Public | Book detail (with nested book_detail) |
| POST | `/` | Admin | Create book |
| PATCH | `/{book_id}` | Admin | Update book |

### POST `/books/` (Admin) – Frontend flow

**Option A: Create book + book_detail in one call**
```json
{
  "title": "Book Title",
  "author": "Author Name",
  "selling_price": 100000,
  "stock_quantity": 10,
  "code": "ISBN123",
  "edition": 1,
  "publication_date": "2024-01-01",
  "book_detail": {
    "description": "Book description",
    "image_url": "https://...",
    "pages": 200,
    "publisher": "Publisher Name",
    "height": 20.5,
    "width": 14.0,
    "weight": 0.3
  }
}
```

**Option B: Create book_detail first, then book**
1. `POST /book-details` → get `{ "id": 1, ... }`
2. `POST /books` with `book_detail_id: 1`

**Option C: Book without detail**
```json
{
  "title": "Book Title",
  "author": "Author",
  "selling_price": 50000,
  "stock_quantity": 5,
  "book_detail_id": null
}
```

### GET `/books/` (paginated)
Query: `?page=1&size=50&q=keyword`
- `page`: page number (default 1)
- `size`: items per page (default 50)
- `q`: search by title, author

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
{
  "title": "Book Title",
  "author": "Author Name",
  "selling_price": 100000,
  "stock_quantity": 10,
  "code": "ISBN123",
  "edition": 1,
  "publication_date": "2024-01-01",
  "book_detail_id": null
}
```

---

## 3b. Book Details (`/book-details`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/` | Admin | List book details |
| GET | `/{detail_id}` | Admin | Book detail by ID |
| POST | `/` | Admin | Create book detail |
| PATCH | `/{detail_id}` | Admin | Update book detail |

### POST `/book-details/` (Admin)
```json
{
  "description": "Book description",
  "image_url": "https://example.com/cover.jpg",
  "pages": 200,
  "publisher": "Publisher Name",
  "height": 20.5,
  "length": 25.0,
  "width": 14.0,
  "weight": 0.3,
  "supplier": "Supplier Name"
}
```
Response: `{ "id": 1, "description": "...", ... }` – use `id` for `book_detail_id` when creating book.

---

## 4. Categories (`/categories`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/` | Public | List categories |
| GET | `/roots` | Public | Root categories |
| GET | `/{category_id}` | Public | Category detail |
| POST | `/` | Admin | Create category |
| PATCH | `/{category_id}` | Admin | Update category |

### POST `/categories/` (Admin)
```json
{ "name": "Fiction", "parent_id": null }
```

---

## 5. Cart (`/cart`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/` | User | User cart |
| POST | `/` | User | Add book to cart |
| PATCH | `/{cart_id}` | User | Update quantity |
| DELETE | `/{cart_id}` | User | Remove item |

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

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/` | User | User orders |
| GET | `/{order_id}` | User | Order detail (own only) |
| POST | `/checkout` | User | Checkout from cart |
| POST | `/` | User | Create order manually |
| PATCH | `/{order_id}/status` | Admin | Update order status |

### POST `/orders/checkout`
```json
{
  "phone_number": "0901234567",
  "shipping_address": "123 Street ABC",
  "note": "Business hours delivery",
  "promotion_code": "SALE10"
}
```

### POST `/orders/` (manual)
```json
{
  "phone_number": "0901234567",
  "shipping_address": "123 Street ABC",
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
Status: `PENDING`, `CONFIRMED`, `INPROGRESS`, `SHIPPED`, `DELIVERED`, `COMPLETED`, `CANCELLED`, `RETURNED`

---

## 7. Reviews (`/reviews`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/book/{book_id}` | Public | Reviews by book |
| GET | `/book/{book_id}/avg` | Public | Average rating |
| POST | `/` | User | Create review |
| PATCH | `/{review_id}` | User | Update (own only) |
| DELETE | `/{review_id}` | User | Delete (own only) |

### POST `/reviews/`
```json
{
  "book_id": 1,
  "content": "Great book!",
  "rate": 5
}
```
`rate`: 1–5

---

## 8. Promotions (`/promotions`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/validate` | Public | Validate promotion code |
| GET | `/` | Admin | List promotions |
| POST | `/` | Admin | Create promotion |
| PATCH | `/{promo_id}` | Admin | Update promotion |

### GET `/promotions/validate`
Query: `?code=SALE10&order_total=100000`

Response:
```json
{
  "valid": true,
  "promotion_id": 1,
  "discount_amount": 10000,
  "name": "10% off"
}
```

### POST `/promotions/` (Admin)
```json
{
  "code": "SALE10",
  "name": "10% off",
  "discount_percent": 10,
  "max_discount": 50000,
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-12-31T23:59:59"
}
```

---

## 9. Return Requests (`/return-requests`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/` | User | User return requests |
| POST | `/` | User | Create return request |
| PATCH | `/{req_id}/process` | Admin | Approve/reject |

### POST `/return-requests/`
```json
{
  "order_id": 1,
  "order_item_id": 1,
  "quantity": 1,
  "reason": "Product defect"
}
```

### PATCH `/return-requests/{req_id}/process` (Admin)
```json
{ "status": "APPROVED" }
```
`status`: `APPROVED`, `REJECTED`

---

## 10. Notifications (`/notifications`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/me` | User | User notifications |
| POST | `/{notification_id}/read` | User | Mark as read |
| GET | `/` | Admin | List notifications |
| POST | `/` | Admin | Create and send notification |

### POST `/notifications/` (Admin)
```json
{
  "user_ids": [1, 2, 3],
  "title": "Order notification",
  "message": "Your order has been confirmed",
  "type": "INFO"
}
```

---

## 11. Support Requests (`/support-requests`)

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| POST | `/` | User | Submit support request |
| GET | `/` | Admin | List support requests |
| PATCH | `/{req_id}` | Admin | Respond to request |

### POST `/support-requests/`
```json
{
  "email": "user@example.com",
  "issue": "Issue title",
  "description": "Detailed description",
  "type": "ORDER"
}
```

### PATCH `/support-requests/{req_id}` (Admin)
```json
{
  "staff_response": "Resolved",
  "status": "RESOLVED"
}
```

---

## 12. Test Utils (`/test`) – Only when TESTING=1 or test.db

| Method | Path | Auth | Description |
|--------|------|------|--------------|
| GET | `/otp` | Public | Get OTP by email (for testing) |
| POST | `/make-admin` | Public | Set is_superuser for user |
| POST | `/books` | Public | Create book without token (for testing) |

### POST `/test/books` (no token)
```json
// Request
{
  "title": "Test Book",
  "author": "Author",
  "selling_price": 50000,
  "stock_quantity": 10,
  "code": "ISBN001",
  "edition": 1,
  "publication_date": "2024-01-01",
  "book_detail_id": null
}
```
Requires `TESTING=1` or `DATABASE_URL` containing `test.db`. Returns 403 if not in test env.

---

## Health Check

| Method | Path | Description |
|--------|------|--------------|
| GET | `/` | `{"message": "Backend Kebook API", "docs": "/docs"}` |
| GET | `/kaithhealthcheck` | `{"status": "ok"}` |
| GET | `/kaithheathcheck` | `{"status": "ok"}` (typo alias) |

---

## Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request – invalid data |
| 401 | Unauthorized – not logged in or token expired. Detail: `"Could not validate credentials"` |
| 403 | Forbidden – insufficient permissions |
| 404 | Not Found – resource not found |
| 500 | Internal Server Error |

### 401 – Could not validate credentials
Occurs when:
- Token missing or invalid
- Token expired
- Token signature invalid (SECRET_KEY changed)
- User deleted or not found

Send token: `Authorization: Bearer <access_token>`
