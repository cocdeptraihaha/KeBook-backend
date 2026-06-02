# Refactor Notification Contract (Backend -> Frontend)

## 1) Mục tiêu

Refactor notification sang mô hình `type + payload`.

- Backend không render nội dung ngôn ngữ tự nhiên.
- Frontend tự xử lý i18n/display theo `type` và `payload`.
- `message` trong DB dùng lưu JSON machine-readable.
- Mỗi trạng thái đơn hàng có 1 `enum` type riêng.
- Review dùng 1 type riêng.

## 2) Phạm vi file đã refactor

- `app/schemas/notification.py`
- `app/services/notification_service.py`
- `app/api/v1/endpoints/notifications.py`
- `app/services/order_service.py`

## 3) NotificationType enum

Khai báo tại `app/schemas/notification.py`:

- `GENERIC`
- `ORDER_NEW`
- `ORDER_SHIPMENT`
- `ORDER_STATUS_PENDING`
- `ORDER_STATUS_CONFIRMED`
- `ORDER_STATUS_INPROGRESS`
- `ORDER_STATUS_SHIPPED`
- `ORDER_STATUS_DELIVERED`
- `ORDER_STATUS_COMPLETED`
- `ORDER_STATUS_CANCELLED`
- `ORDER_STATUS_CANCEL_REQUESTED`
- `ORDER_STATUS_RETURNED`
- `REVIEW_NEW`
- `SUPPORT_NEW`

## 4) Quy ước dữ liệu

### 4.1 DB storage

Bảng notification vẫn giữ schema cũ:

- `notification.type` lưu string enum.
- `notification.message` lưu JSON string payload.

Ví dụ `message`:

```json
{"order_id": 32, "status": "CONFIRMED"}
```

### 4.2 API response cho user notifications

`GET /api/v1/notifications/me` trả `list[UserNotificationOut]`.

Mỗi item:

```json
{
  "notification_id": 101,
  "user_id": 12,
  "is_read": false,
  "read_at": null,
  "notification": {
    "id": 88,
    "title": "ORDER #32",
    "message": "{\"order_id\":32,\"status\":\"CONFIRMED\"}",
    "type": "ORDER_STATUS_CONFIRMED",
    "send_date": "2026-05-27T13:00:00",
    "deleted_at": null,
    "payload": {
      "order_id": 32,
      "status": "CONFIRMED"
    }
  }
}
```

Ghi chú:

- Frontend nên dùng `notification.payload`, không parse `message` thủ công.
- `message` giữ để tương thích/backward.

### 4.3 WebSocket payload

Server push event `new_notification` gồm:

- `type`: `new_notification`
- `schema_version`
- `id`
- `title`
- `message`
- `notif_type`
- `send_date`
- `unread_count`
- `payload`
- `meta` (alias của payload để tương thích)

Ví dụ:

```json
{
  "type": "new_notification",
  "schema_version": 2,
  "id": 88,
  "title": "ORDER #32",
  "message": "{\"order_id\":32,\"status\":\"CONFIRMED\"}",
  "notif_type": "ORDER_STATUS_CONFIRMED",
  "send_date": "2026-05-27T13:00:00",
  "unread_count": 5,
  "payload": {
    "order_id": 32,
    "status": "CONFIRMED"
  },
  "meta": {
    "order_id": 32,
    "status": "CONFIRMED"
  }
}
```

## 5) Mapping nghiệp vụ đã áp dụng

### 5.1 Đơn hàng

#### a) Buyer đặt đơn

- Type: `ORDER_NEW`
- Payload:

```json
{"order_id": 32}
```

#### b) Buyer nhận cập nhật trạng thái

Map `status -> type`:

- `PENDING -> ORDER_STATUS_PENDING`
- `CONFIRMED -> ORDER_STATUS_CONFIRMED`
- `INPROGRESS -> ORDER_STATUS_INPROGRESS`
- `SHIPPED -> ORDER_STATUS_SHIPPED`
- `DELIVERED -> ORDER_STATUS_DELIVERED`
- `COMPLETED -> ORDER_STATUS_COMPLETED`
- `CANCELLED -> ORDER_STATUS_CANCELLED`
- `CANCEL_REQUESTED -> ORDER_STATUS_CANCEL_REQUESTED`
- `RETURNED -> ORDER_STATUS_RETURNED`

Payload:

```json
{"order_id": 32, "status": "CONFIRMED"}
```

#### c) Update shipment

- Type: `ORDER_SHIPMENT`
- Payload:

```json
{
  "order_id": 32,
  "tracking_number": "VN123456789",
  "shipping_provider": "GHN"
}
```

#### d) Admin nhận đơn mới

- Type: `ORDER_NEW`
- Payload:

```json
{"order_id": 32}
```

### 5.2 Review

Admin nhận review mới:

- Type: `REVIEW_NEW`
- Payload:

```json
{"book_id": 10, "review_id": 55}
```

### 5.3 Support

Admin nhận support ticket mới:

- Type: `SUPPORT_NEW`
- Payload:

```json
{"support_id": 77}
```

## 6) Backward compatibility

Service parser có fallback:

- Ưu tiên parse `message` dạng JSON.
- Nếu không phải JSON, parse legacy format `key:value` từng dòng.

Mục tiêu:

- Notification cũ vẫn đọc được `payload` cơ bản.
- Frontend migrate dần, không cần big-bang.

## 7) Contract frontend đề xuất

## 7.1 Rendering flow

1. Nhận notification item.
2. Lấy `type` (`notification.type` hoặc `notif_type` từ WS).
3. Lấy `payload`.
4. Lookup dictionary i18n theo `type`.
5. Bind biến từ `payload` vào template.

## 7.2 Gợi ý i18n key

- `notification.ORDER_NEW`
- `notification.ORDER_SHIPMENT`
- `notification.ORDER_STATUS_PENDING`
- `notification.ORDER_STATUS_CONFIRMED`
- `notification.ORDER_STATUS_INPROGRESS`
- `notification.ORDER_STATUS_SHIPPED`
- `notification.ORDER_STATUS_DELIVERED`
- `notification.ORDER_STATUS_COMPLETED`
- `notification.ORDER_STATUS_CANCELLED`
- `notification.ORDER_STATUS_CANCEL_REQUESTED`
- `notification.ORDER_STATUS_RETURNED`
- `notification.REVIEW_NEW`
- `notification.SUPPORT_NEW`

## 7.3 Fallback UI

Nếu `type` lạ:

- Render generic title/body.
- Log telemetry để bổ sung mapping.

## 8) Những điểm không đổi

- Không đổi DB schema notification.
- Không đổi flow mark read/unread count.
- Không đổi route read-all/read-one.

## 9) Test checklist nhanh

- Tạo order mới: buyer + admin nhận `ORDER_NEW` payload đúng.
- Update status từng bước: type khớp enum tương ứng.
- Update shipment: nhận `ORDER_SHIPMENT` có `tracking_number`, `shipping_provider`.
- Tạo review: admin nhận `REVIEW_NEW` có `book_id`, `review_id`.
- API `/notifications/me`: có `notification.payload` parse đúng.
- WS event: có `payload` và `meta` cùng giá trị.

## 10) Lưu ý triển khai tiếp

- Nếu muốn query/filter theo payload trong DB, cân nhắc migrate `message` sang JSON column tương lai.
- Nếu mở rộng domain event mới, thêm enum + payload schema rõ ràng trước khi dùng.
