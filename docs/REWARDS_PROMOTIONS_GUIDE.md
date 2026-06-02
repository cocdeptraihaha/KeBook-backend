# Hướng Dẫn Hệ Thống Khuyến Mãi Và Đổi Điểm

Base URL: `http://localhost:8000/api/v1`

Auth:

- User APIs cần `Authorization: Bearer <access_token>`.
- Admin APIs cần user có `is_superuser = true`.

## 1. Migration Database

Nếu DB chưa có loyalty/rewards:

```sql
migrations/add_loyalty_points_favorites_vouchers.sql
```

Sau đó chạy upgrade mới:

```sql
migrations/upgrade_rewards_promotions.sql
```

Nếu muốn seed dữ liệu giống màn Rewards:

```sql
scripts/seed_point_rewards.sql
```

Lưu ý: các file `ALTER TABLE` không idempotent hoàn toàn. Nếu cột đã tồn tại, không chạy lại nguyên file.

## 2. Reward Types

`point_rewards.reward_type` hỗ trợ 3 loại:

| Type | Ý nghĩa | Field chính |
|------|---------|-------------|
| `DISCOUNT_PERCENT` | Giảm theo phần trăm | `discount_percent`, `max_discount` |
| `DISCOUNT_AMOUNT` | Giảm số tiền cố định | `discount_amount` |
| `FREE_SHIPPING` | Miễn phí vận chuyển | `free_shipping` trong promotion sau khi đổi |

Field hiển thị cho màn Rewards:

- `name`: tên voucher.
- `description`: mô tả điều kiện.
- `icon`: gợi ý icon frontend, ví dụ `ticket-percent`, `truck`, `gift`.
- `cost_points`: điểm cần có.
- `usage_limit`: tổng lượt có thể đổi.
- `used_count`: số lượt đã đổi.
- Remaining frontend tự tính: `usage_limit - used_count`.

## 3. Lấy Điểm Hiện Có

```http
GET /users/me/points
```

Response:

```json
{
  "balance": 1250
}
```

## 4. Lấy Danh Sách Rewards

```http
GET /points/rewards
```

Response:

```json
[
  {
    "id": 1,
    "name": "Voucher giảm 50.000đ",
    "description": "Giảm 50.000đ cho đơn hàng từ 500.000đ",
    "reward_type": "DISCOUNT_AMOUNT",
    "icon": "ticket-percent",
    "cost_points": 500,
    "discount_percent": null,
    "discount_amount": 50000,
    "max_discount": null,
    "min_order_amount": 500000,
    "usage_limit": 1250,
    "used_count": 0,
    "valid_days": 30,
    "active": true,
    "created_at": "2026-06-02T10:00:00"
  }
]
```

## 5. Đổi Điểm Lấy Voucher

```http
POST /points/rewards/{reward_id}/redeem
```

Response:

```json
{
  "promotion_id": 10,
  "code": "PT1UABC123",
  "name": "Voucher giảm 50.000đ (doi diem)",
  "discount_percent": null,
  "discount_amount": 50000,
  "free_shipping": false,
  "max_discount": null,
  "min_order_amount": 500000,
  "end_date": "2026-07-02T10:00:00",
  "points_balance_after": 750
}
```

Rules:

- Không đủ điểm: `400`.
- Reward hết lượt: `400`.
- User đã đổi reward đó rồi: `400`.
- Voucher sinh ra là voucher cá nhân, chỉ user đó dùng được.

## 6. Checkout Bằng Voucher

```http
POST /orders/checkout
```

Request:

```json
{
  "promotion_code": "PT1UABC123",
  "phone_number": "0901234567",
  "shipping_address": "12 Nguyen Trai",
  "ward": "Ben Thanh",
  "province": "Ho Chi Minh"
}
```

Backend tự validate:

- Mã tồn tại và chưa hết hạn.
- Nếu là voucher cá nhân, current user phải là owner.
- Đơn đạt `min_order_amount`.
- Voucher chưa hết `usage_limit`.
- Voucher chưa từng dùng trong đơn trước đó của user.

Discount:

- `DISCOUNT_AMOUNT`: trừ `discount_amount`.
- `DISCOUNT_PERCENT`: trừ theo `discount_percent`, giới hạn bởi `max_discount`.
- `FREE_SHIPPING`: set `shipping_fee = 0`.

## 7. Admin Tạo Reward

```http
POST /points/admin/rewards
```

Fixed amount:

```json
{
  "name": "Voucher giảm 50.000đ",
  "description": "Giảm 50.000đ cho đơn hàng từ 500.000đ",
  "reward_type": "DISCOUNT_AMOUNT",
  "icon": "ticket-percent",
  "cost_points": 500,
  "discount_amount": 50000,
  "min_order_amount": 500000,
  "usage_limit": 1250,
  "valid_days": 30,
  "active": true
}
```

Free shipping:

```json
{
  "name": "Miễn phí vận chuyển",
  "description": "Miễn phí vận chuyển cho đơn hàng từ 300.000đ",
  "reward_type": "FREE_SHIPPING",
  "icon": "truck",
  "cost_points": 300,
  "min_order_amount": 300000,
  "usage_limit": 2000,
  "valid_days": 30,
  "active": true
}
```

Percent:

```json
{
  "name": "Voucher giảm 20%",
  "description": "Giảm 20% tối đa 200.000đ cho đơn hàng từ 1.200.000đ",
  "reward_type": "DISCOUNT_PERCENT",
  "icon": "gift",
  "cost_points": 1500,
  "discount_percent": 20,
  "max_discount": 200000,
  "min_order_amount": 1200000,
  "usage_limit": 450,
  "valid_days": 30,
  "active": true
}
```

## 8. Admin Cập Nhật Reward

```http
PATCH /points/admin/rewards/{reward_id}
```

Request gửi field cần sửa:

```json
{
  "active": false,
  "usage_limit": 2000
}
```

## 9. API Cần Cho Screen Rewards

Load screen:

1. `GET /users/me/points`
2. `GET /points/rewards`

Nhấn "Đổi ngay":

1. Check `balance >= cost_points`.
2. Check `usage_limit == null || used_count < usage_limit`.
3. Call `POST /points/rewards/{reward_id}/redeem`.
4. Refresh balance and rewards list.

Hiển thị còn lại:

```ts
const remaining = usage_limit == null ? null : Math.max(0, usage_limit - used_count)
```
