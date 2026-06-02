# Hướng Dẫn Sử Dụng Sổ Địa Chỉ

Base URL: `http://localhost:8000/api/v1`

Auth: các API sổ địa chỉ cần header `Authorization: Bearer <access_token>`.

## 1. Cập Nhật Database

Chạy migration một lần trên database hiện hữu:

```sql
-- file
migrations/add_user_addresses.sql
```

Migration tạo bảng `user_addresses`, thêm `orders.address_id`, và backfill 1 địa chỉ mặc định từ thông tin cũ trong bảng `users` nếu user đã có `full_name`, `phone_number`, `address`, `ward`, hoặc `province`.

Lưu ý: file SQL này không idempotent hoàn toàn cho phần `ALTER TABLE orders ADD COLUMN address_id`. Không chạy lại lần 2 nếu cột đã tồn tại.

## 2. Cấu Trúc Địa Chỉ

Mỗi địa chỉ có các field:

```json
{
  "id": 1,
  "user_id": 10,
  "label": "Nhà riêng",
  "recipient_name": "Nguyen Van A",
  "phone_number": "0901234567",
  "address_detail": "12 Nguyen Trai",
  "ward": "Ben Thanh",
  "province": "Ho Chi Minh",
  "is_default": true,
  "created_at": "2026-06-02T10:00:00",
  "updated_at": "2026-06-02T10:00:00",
  "deleted_at": null
}
```

Mapping nghiệp vụ:

- `label`: Tên gợi nhớ địa chỉ, ví dụ "Nhà riêng", "Công ty".
- `recipient_name`: Tên người nhận.
- `phone_number`: Số điện thoại người nhận.
- `address_detail`: Số nhà, tên đường, địa chỉ chi tiết.
- `ward`: Xã/Phường.
- `province`: Tỉnh/Thành phố.
- `is_default`: Địa chỉ mặc định của user.

## 3. API Lookup Tỉnh/Phường

### Lấy danh sách tỉnh/thành

```http
GET /addresses/provinces
```

Response:

```json
[
  { "code": 1, "name": "Thành phố Hà Nội" }
]
```

### Lấy danh sách xã/phường theo tỉnh

```http
GET /addresses/wards?province_id=1
```

Response:

```json
[
  { "code": 101, "name": "Phường ..." }
]
```

## 4. API Sổ Địa Chỉ

### Lấy sổ địa chỉ của user

```http
GET /addresses/me
```

Response:

```json
[
  {
    "id": 1,
    "user_id": 10,
    "label": "Nhà riêng",
    "recipient_name": "Nguyen Van A",
    "phone_number": "0901234567",
    "address_detail": "12 Nguyen Trai",
    "ward": "Ben Thanh",
    "province": "Ho Chi Minh",
    "is_default": true,
    "created_at": "2026-06-02T10:00:00",
    "updated_at": "2026-06-02T10:00:00",
    "deleted_at": null
  }
]
```

### Tạo địa chỉ mới

```http
POST /addresses/me
```

Request:

```json
{
  "label": "Nhà riêng",
  "recipient_name": "Nguyen Van A",
  "phone_number": "0901234567",
  "address_detail": "12 Nguyen Trai",
  "ward": "Ben Thanh",
  "province": "Ho Chi Minh",
  "is_default": true
}
```

Nếu thiếu `recipient_name`, backend lấy mặc định từ `current_user.full_name`.

Nếu thiếu `phone_number`, backend lấy mặc định từ `current_user.phone_number`.

Nếu user chưa có địa chỉ nào, địa chỉ đầu tiên tự thành mặc định.

### Cập nhật địa chỉ

```http
PATCH /addresses/me/{address_id}
```

Request chỉ cần gửi field muốn đổi:

```json
{
  "label": "Công ty",
  "recipient_name": "Tran Thi B",
  "phone_number": "0909999999",
  "address_detail": "99 Le Loi",
  "ward": "Ward 1",
  "province": "Ha Noi",
  "is_default": true
}
```

Nếu set `is_default = true`, các địa chỉ khác của user tự chuyển `is_default = false`.

### Đặt địa chỉ mặc định

```http
PATCH /addresses/me/{address_id}/default
```

Response là địa chỉ vừa được đặt mặc định.

### Xóa địa chỉ

```http
DELETE /addresses/me/{address_id}
```

Xóa mềm bằng `deleted_at`. Response status: `204 No Content`.

Nếu xóa địa chỉ mặc định, backend tự chọn địa chỉ còn lại mới nhất làm mặc định.

## 5. Checkout Với Sổ Địa Chỉ

Checkout mới hỗ trợ `address_id`:

```http
POST /orders/checkout
```

Request:

```json
{
  "address_id": 1,
  "promotion_code": "SALE10",
  "loyalty_points_to_redeem": 200
}
```

Backend validate địa chỉ thuộc current user và chưa bị xóa. Nếu hợp lệ, order snapshot:

- `orders.address_id` = id địa chỉ đã chọn.
- `orders.full_name` = `recipient_name`.
- `orders.phone_number` = `phone_number`.
- `orders.shipping_address` = `address_detail, ward, province`.

Response order có thêm `address_id`:

```json
{
  "order": {
    "id": 100,
    "address_id": 1,
    "full_name": "Nguyen Van A",
    "phone_number": "0901234567",
    "shipping_address": "12 Nguyen Trai, Ben Thanh, Ho Chi Minh",
    "status": "PENDING"
  },
  "item_amount": 100000,
  "discount_total": 0,
  "shipping_fee": 0,
  "total_amount": 100000
}
```

## 6. Override Khi Checkout

Frontend vẫn có thể gửi field thủ công để override địa chỉ đã lưu cho riêng order đó:

```json
{
  "address_id": 1,
  "full_name": "Nguoi Nhan Khac",
  "phone_number": "0911111111",
  "shipping_address": "88 Tran Phu",
  "ward": "Ward 8",
  "province": "Da Nang"
}
```

Ưu tiên snapshot:

1. Field gửi trong checkout nếu có giá trị.
2. Field từ địa chỉ đã lưu.
3. Riêng `full_name` fallback thêm từ `current_user.full_name`.

## 7. Checkout Cũ Vẫn Dùng Được

Không bắt buộc dùng `address_id`. Request cũ vẫn hợp lệ:

```json
{
  "phone_number": "0901234567",
  "shipping_address": "12 Nguyen Trai",
  "ward": "Ben Thanh",
  "province": "Ho Chi Minh",
  "note": "Giao giờ hành chính"
}
```

Trong trường hợp này:

- `orders.address_id` = `null`.
- `orders.shipping_address` vẫn ghép từ `shipping_address`, `ward`, `province`.
- Không tạo mới địa chỉ trong sổ địa chỉ.

## 8. Lỗi Thường Gặp

### Dùng địa chỉ không thuộc user

```json
{
  "detail": "Address not found"
}
```

Status: `400` khi checkout, `404` khi sửa/xóa/set default.

### Thiếu token

```json
{
  "detail": "Not authenticated"
}
```

Status: `401`.

## 9. Gợi Ý Flow Frontend

1. User vào trang checkout.
2. Gọi `GET /addresses/me`.
3. Nếu có địa chỉ, chọn địa chỉ `is_default = true`.
4. Nếu chưa có địa chỉ, hiển thị form tạo địa chỉ.
5. Khi user bấm đặt hàng, gửi `address_id`.
6. Nếu user sửa nhanh thông tin người nhận trong checkout, gửi thêm các field override.
