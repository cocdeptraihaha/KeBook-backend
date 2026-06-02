# Frontend Response Contract (Auto Generated)

Ngu?n: OpenAPI t? backend hi?n t?i (`app.main:app`).
M?c ti?u: frontend bi?t JSON response cho m?i route/status ?? map UI state/loading/error ch?nh x?c.

## Global Notes
- Auth header (route c?n auth): `Authorization: Bearer <token>`. 
- Nhi?u route c? th? tr? `401/403/404/422` t?y context.
- `204` ngh?a l? kh?ng c? body.

## `/`

### `GET /`
- Summary: Root
- OperationId: `root__get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

## `/api/v1/addresses/provinces`

### `GET /api/v1/addresses/provinces`
- Summary: List Provinces
- OperationId: `list_provinces_api_v1_addresses_provinces_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "code": 0,
    "name": "string"
  }
]
```

## `/api/v1/addresses/wards`

### `GET /api/v1/addresses/wards`
- Summary: List Wards
- OperationId: `list_wards_api_v1_addresses_wards_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "code": 0,
    "name": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/admin/dashboard/by-category`

### `GET /api/v1/admin/dashboard/by-category`
- Summary: Dashboard By Category
- OperationId: `dashboard_by_category_api_v1_admin_dashboard_by_category_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "category_id": 0,
    "category_name": "string",
    "revenue": 0,
    "order_count": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/admin/dashboard/cancellation-timeseries`

### `GET /api/v1/admin/dashboard/cancellation-timeseries`
- Summary: Dashboard Cancellation Timeseries
- OperationId: `dashboard_cancellation_timeseries_api_v1_admin_dashboard_cancellation_timeseries_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "period": "string",
    "total_orders": 0,
    "cancelled_count": 0,
    "cancel_rate": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/admin/dashboard/order-status-breakdown`

### `GET /api/v1/admin/dashboard/order-status-breakdown`
- Summary: Dashboard Order Status Breakdown
- OperationId: `dashboard_order_status_breakdown_api_v1_admin_dashboard_order_status_breakdown_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "status": "string",
    "count": 0,
    "revenue": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/admin/dashboard/revenue.csv`

### `GET /api/v1/admin/dashboard/revenue.csv`
- Summary: Dashboard Revenue Csv
- OperationId: `dashboard_revenue_csv_api_v1_admin_dashboard_revenue_csv_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/admin/dashboard/summary`

### `GET /api/v1/admin/dashboard/summary`
- Summary: Dashboard Summary
- OperationId: `dashboard_summary_api_v1_admin_dashboard_summary_get`

#### Status `200`
- Description: Successful Response
```json
{
  "revenue": 0,
  "order_count": 0,
  "aov": 0,
  "new_user_count": 0,
  "low_stock_count": 0,
  "pending_order_count": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/admin/dashboard/top-books`

### `GET /api/v1/admin/dashboard/top-books`
- Summary: Dashboard Top Books
- OperationId: `dashboard_top_books_api_v1_admin_dashboard_top_books_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "book_id": 0,
    "title": "string",
    "quantity_sold": 0,
    "revenue": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/admin/dashboard/top-customers`

### `GET /api/v1/admin/dashboard/top-customers`
- Summary: Dashboard Top Customers
- OperationId: `dashboard_top_customers_api_v1_admin_dashboard_top_customers_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "user_id": 0,
    "full_name": "string",
    "email": "string",
    "order_count": 0,
    "total_spent": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/admin/dashboard/user-timeseries`

### `GET /api/v1/admin/dashboard/user-timeseries`
- Summary: Dashboard User Timeseries
- OperationId: `dashboard_user_timeseries_api_v1_admin_dashboard_user_timeseries_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "period": "string",
    "new_users": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/auth/forgot-password`

### `POST /api/v1/auth/forgot-password`
- Summary: Forgot Password
- OperationId: `forgot_password_api_v1_auth_forgot_password_post`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/auth/login`

### `POST /api/v1/auth/login`
- Summary: Login
- OperationId: `login_api_v1_auth_login_post`

#### Status `200`
- Description: Successful Response
```json
{
  "access_token": "string",
  "token_type": "string",
  "user": {
    "email": "user@example.com",
    "username": "string",
    "full_name": "string",
    "address": "string",
    "province": "string",
    "ward": "string",
    "avatar_url": "string",
    "date_of_birth": "2026-01-01T00:00:00Z",
    "gender": "string",
    "phone_number": "string",
    "id": 0,
    "is_active": false,
    "is_superuser": false,
    "loyalty_points": 0,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/auth/register`

### `POST /api/v1/auth/register`
- Summary: Register
- OperationId: `register_api_v1_auth_register_post`

#### Status `201`
- Description: Successful Response
```json
{
  "message": "string",
  "email": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/auth/resend-otp`

### `POST /api/v1/auth/resend-otp`
- Summary: Resend Otp
- OperationId: `resend_otp_api_v1_auth_resend_otp_post`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/auth/reset-password`

### `POST /api/v1/auth/reset-password`
- Summary: Reset Password
- OperationId: `reset_password_api_v1_auth_reset_password_post`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/auth/verify-otp`

### `POST /api/v1/auth/verify-otp`
- Summary: Verify Otp
- OperationId: `verify_otp_api_v1_auth_verify_otp_post`

#### Status `200`
- Description: Successful Response
```json
{
  "access_token": "string",
  "token_type": "string",
  "user": {
    "email": "user@example.com",
    "username": "string",
    "full_name": "string",
    "address": "string",
    "province": "string",
    "ward": "string",
    "avatar_url": "string",
    "date_of_birth": "2026-01-01T00:00:00Z",
    "gender": "string",
    "phone_number": "string",
    "id": 0,
    "is_active": false,
    "is_superuser": false,
    "loyalty_points": 0,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/book-details/`

### `GET /api/v1/book-details/`
- Summary: List Book Details
- OperationId: `list_book_details_api_v1_book_details__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "description": "string",
    "height": 0,
    "image_url": "string",
    "length": 0,
    "pages": 0,
    "publisher": "string",
    "supplier": "string",
    "weight": 0,
    "width": 0,
    "id": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/book-details/`
- Summary: Create Book Detail
- OperationId: `create_book_detail_api_v1_book_details__post`

#### Status `201`
- Description: Successful Response
```json
{
  "description": "string",
  "height": 0,
  "image_url": "string",
  "length": 0,
  "pages": 0,
  "publisher": "string",
  "supplier": "string",
  "weight": 0,
  "width": 0,
  "id": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/book-details/{detail_id}`

### `GET /api/v1/book-details/{detail_id}`
- Summary: Get Book Detail
- OperationId: `get_book_detail_api_v1_book_details__detail_id__get`

#### Status `200`
- Description: Successful Response
```json
{
  "description": "string",
  "height": 0,
  "image_url": "string",
  "length": 0,
  "pages": 0,
  "publisher": "string",
  "supplier": "string",
  "weight": 0,
  "width": 0,
  "id": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/book-details/{detail_id}`
- Summary: Update Book Detail
- OperationId: `update_book_detail_api_v1_book_details__detail_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "description": "string",
  "height": 0,
  "image_url": "string",
  "length": 0,
  "pages": 0,
  "publisher": "string",
  "supplier": "string",
  "weight": 0,
  "width": 0,
  "id": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/book-discounts/`

### `GET /api/v1/book-discounts/`
- Summary: List Book Discounts
- OperationId: `list_book_discounts_api_v1_book_discounts__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "id": 0,
    "discount_amount": 0,
    "discount_percent": 0,
    "start_date": "2026-01-01T00:00:00Z",
    "end_date": "2026-01-01T00:00:00Z",
    "book_ids": [
      0
    ]
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/book-discounts/`
- Summary: Create Book Discount
- OperationId: `create_book_discount_api_v1_book_discounts__post`

#### Status `201`
- Description: Successful Response
```json
{
  "id": 0,
  "discount_amount": 0,
  "discount_percent": 0,
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-01T00:00:00Z",
  "book_ids": [
    0
  ]
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/book-discounts/{discount_id}`

### `DELETE /api/v1/book-discounts/{discount_id}`
- Summary: Delete Book Discount
- OperationId: `delete_book_discount_api_v1_book_discounts__discount_id__delete`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/book-discounts/{discount_id}`
- Summary: Update Book Discount
- OperationId: `update_book_discount_api_v1_book_discounts__discount_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "id": 0,
  "discount_amount": 0,
  "discount_percent": 0,
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-01T00:00:00Z",
  "book_ids": [
    0
  ]
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/`

### `GET /api/v1/books/`
- Summary: List Books
- OperationId: `list_books_api_v1_books__get`

#### Status `200`
- Description: Successful Response
```json
{
  "items": [
    {
      "author": "string",
      "code": "string",
      "edition": 0,
      "publication_date": "2026-01-01",
      "selling_price": 0,
      "stock_quantity": 0,
      "title": "string",
      "book_detail_id": 0,
      "id": 0,
      "deleted_at": "2026-01-01T00:00:00Z",
      "images": [
        {
          "image_url": "string",
          "sort_order": 0,
          "is_primary": false,
          "alt_text": "string",
          "id": 0,
          "book_id": 0
        }
      ],
      "original_price": 0,
      "discount_amount": 0,
      "discount_percent": 0,
      "has_discount": false,
      "final_price": 0,
      "image_url": "string"
    }
  ],
  "total": 0,
  "page": 0,
  "size": 0,
  "pages": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/books/`
- Summary: Create Book
- OperationId: `create_book_api_v1_books__post`

#### Status `201`
- Description: Successful Response
```json
{
  "author": "string",
  "code": "string",
  "edition": 0,
  "publication_date": "2026-01-01",
  "selling_price": 0,
  "stock_quantity": 0,
  "title": "string",
  "book_detail_id": 0,
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "images": [
    {
      "image_url": "string",
      "sort_order": 0,
      "is_primary": false,
      "alt_text": "string",
      "id": 0,
      "book_id": 0
    }
  ],
  "original_price": 0,
  "discount_amount": 0,
  "discount_percent": 0,
  "has_discount": false,
  "final_price": 0,
  "image_url": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/admin/all`

### `GET /api/v1/books/admin/all`
- Summary: Admin List Books
- OperationId: `admin_list_books_api_v1_books_admin_all_get`

#### Status `200`
- Description: Successful Response
```json
{
  "items": [
    {
      "author": "string",
      "code": "string",
      "edition": 0,
      "publication_date": "2026-01-01",
      "selling_price": 0,
      "stock_quantity": 0,
      "title": "string",
      "book_detail_id": 0,
      "id": 0,
      "deleted_at": "2026-01-01T00:00:00Z",
      "images": [
        {
          "image_url": "string",
          "sort_order": 0,
          "is_primary": false,
          "alt_text": "string",
          "id": 0,
          "book_id": 0
        }
      ],
      "original_price": 0,
      "discount_amount": 0,
      "discount_percent": 0,
      "has_discount": false,
      "final_price": 0,
      "image_url": "string"
    }
  ],
  "total": 0,
  "page": 0,
  "size": 0,
  "pages": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/admin/low-stock`

### `GET /api/v1/books/admin/low-stock`
- Summary: Admin Low Stock Books
- OperationId: `admin_low_stock_books_api_v1_books_admin_low_stock_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "author": "string",
    "code": "string",
    "edition": 0,
    "publication_date": "2026-01-01",
    "selling_price": 0,
    "stock_quantity": 0,
    "title": "string",
    "book_detail_id": 0,
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "images": [
      {
        "image_url": "string",
        "sort_order": 0,
        "is_primary": false,
        "alt_text": "string",
        "id": 0,
        "book_id": 0
      }
    ],
    "original_price": 0,
    "discount_amount": 0,
    "discount_percent": 0,
    "has_discount": false,
    "final_price": 0,
    "image_url": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/top-discounted`

### `GET /api/v1/books/top-discounted`
- Summary: Top Discounted Books
- OperationId: `top_discounted_books_api_v1_books_top_discounted_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "author": "string",
    "code": "string",
    "edition": 0,
    "publication_date": "2026-01-01",
    "selling_price": 0,
    "stock_quantity": 0,
    "title": "string",
    "book_detail_id": 0,
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "images": [
      {
        "image_url": "string",
        "sort_order": 0,
        "is_primary": false,
        "alt_text": "string",
        "id": 0,
        "book_id": 0
      }
    ],
    "original_price": 0,
    "discount_amount": 0,
    "discount_percent": 0,
    "has_discount": false,
    "final_price": 0,
    "image_url": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/top-selling`

### `GET /api/v1/books/top-selling`
- Summary: Top Selling Books
- OperationId: `top_selling_books_api_v1_books_top_selling_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "author": "string",
    "code": "string",
    "edition": 0,
    "publication_date": "2026-01-01",
    "selling_price": 0,
    "stock_quantity": 0,
    "title": "string",
    "book_detail_id": 0,
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "images": [
      {
        "image_url": "string",
        "sort_order": 0,
        "is_primary": false,
        "alt_text": "string",
        "id": 0,
        "book_id": 0
      }
    ],
    "original_price": 0,
    "discount_amount": 0,
    "discount_percent": 0,
    "has_discount": false,
    "final_price": 0,
    "image_url": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/{book_id}`

### `DELETE /api/v1/books/{book_id}`
- Summary: Soft Delete Book
- OperationId: `soft_delete_book_api_v1_books__book_id__delete`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `GET /api/v1/books/{book_id}`
- Summary: Get Book
- OperationId: `get_book_api_v1_books__book_id__get`

#### Status `200`
- Description: Successful Response
```json
{
  "author": "string",
  "code": "string",
  "edition": 0,
  "publication_date": "2026-01-01",
  "selling_price": 0,
  "stock_quantity": 0,
  "title": "string",
  "book_detail_id": 0,
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "book_detail": {
    "description": "string",
    "height": 0,
    "image_url": "string",
    "length": 0,
    "pages": 0,
    "publisher": "string",
    "supplier": "string",
    "weight": 0,
    "width": 0,
    "id": 0
  },
  "images": [
    {
      "image_url": "string",
      "sort_order": 0,
      "is_primary": false,
      "alt_text": "string",
      "id": 0,
      "book_id": 0
    }
  ],
  "buyer_count": 0,
  "review_count": 0,
  "view_count": 0,
  "original_price": 0,
  "discount_amount": 0,
  "discount_percent": 0,
  "has_discount": false,
  "final_price": 0,
  "image_url": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/books/{book_id}`
- Summary: Update Book
- OperationId: `update_book_api_v1_books__book_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "author": "string",
  "code": "string",
  "edition": 0,
  "publication_date": "2026-01-01",
  "selling_price": 0,
  "stock_quantity": 0,
  "title": "string",
  "book_detail_id": 0,
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "images": [
    {
      "image_url": "string",
      "sort_order": 0,
      "is_primary": false,
      "alt_text": "string",
      "id": 0,
      "book_id": 0
    }
  ],
  "original_price": 0,
  "discount_amount": 0,
  "discount_percent": 0,
  "has_discount": false,
  "final_price": 0,
  "image_url": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/{book_id}/categories`

### `PUT /api/v1/books/{book_id}/categories`
- Summary: Put Book Categories
- OperationId: `put_book_categories_api_v1_books__book_id__categories_put`

#### Status `200`
- Description: Successful Response
```json
{
  "author": "string",
  "code": "string",
  "edition": 0,
  "publication_date": "2026-01-01",
  "selling_price": 0,
  "stock_quantity": 0,
  "title": "string",
  "book_detail_id": 0,
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "images": [
    {
      "image_url": "string",
      "sort_order": 0,
      "is_primary": false,
      "alt_text": "string",
      "id": 0,
      "book_id": 0
    }
  ],
  "original_price": 0,
  "discount_amount": 0,
  "discount_percent": 0,
  "has_discount": false,
  "final_price": 0,
  "image_url": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/{book_id}/images`

### `GET /api/v1/books/{book_id}/images`
- Summary: List Book Images
- OperationId: `list_book_images_api_v1_books__book_id__images_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "image_url": "string",
    "sort_order": 0,
    "is_primary": false,
    "alt_text": "string",
    "id": 0,
    "book_id": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/books/{book_id}/images`
- Summary: Create Book Image
- OperationId: `create_book_image_api_v1_books__book_id__images_post`

#### Status `201`
- Description: Successful Response
```json
{
  "image_url": "string",
  "sort_order": 0,
  "is_primary": false,
  "alt_text": "string",
  "id": 0,
  "book_id": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/{book_id}/images/{image_id}`

### `DELETE /api/v1/books/{book_id}/images/{image_id}`
- Summary: Delete Book Image
- OperationId: `delete_book_image_api_v1_books__book_id__images__image_id__delete`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/books/{book_id}/images/{image_id}`
- Summary: Update Book Image
- OperationId: `update_book_image_api_v1_books__book_id__images__image_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "image_url": "string",
  "sort_order": 0,
  "is_primary": false,
  "alt_text": "string",
  "id": 0,
  "book_id": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/{book_id}/restore`

### `POST /api/v1/books/{book_id}/restore`
- Summary: Restore Book
- OperationId: `restore_book_api_v1_books__book_id__restore_post`

#### Status `200`
- Description: Successful Response
```json
{
  "author": "string",
  "code": "string",
  "edition": 0,
  "publication_date": "2026-01-01",
  "selling_price": 0,
  "stock_quantity": 0,
  "title": "string",
  "book_detail_id": 0,
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "images": [
    {
      "image_url": "string",
      "sort_order": 0,
      "is_primary": false,
      "alt_text": "string",
      "id": 0,
      "book_id": 0
    }
  ],
  "original_price": 0,
  "discount_amount": 0,
  "discount_percent": 0,
  "has_discount": false,
  "final_price": 0,
  "image_url": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/{book_id}/similar`

### `GET /api/v1/books/{book_id}/similar`
- Summary: Similar Books
- OperationId: `similar_books_api_v1_books__book_id__similar_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "author": "string",
    "code": "string",
    "edition": 0,
    "publication_date": "2026-01-01",
    "selling_price": 0,
    "stock_quantity": 0,
    "title": "string",
    "book_detail_id": 0,
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "images": [
      {
        "image_url": "string",
        "sort_order": 0,
        "is_primary": false,
        "alt_text": "string",
        "id": 0,
        "book_id": 0
      }
    ],
    "original_price": 0,
    "discount_amount": 0,
    "discount_percent": 0,
    "has_discount": false,
    "final_price": 0,
    "image_url": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/books/{book_id}/view`

### `POST /api/v1/books/{book_id}/view`
- Summary: Record Book View
- OperationId: `record_book_view_api_v1_books__book_id__view_post`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/cart/`

### `GET /api/v1/cart/`
- Summary: Get My Cart
- OperationId: `get_my_cart_api_v1_cart__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "quantity": 0,
    "book_id": 0,
    "user_id": 0,
    "id": 0,
    "create_at": "2026-01-01",
    "update_at": "2026-01-01"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/cart/`
- Summary: Add To Cart
- OperationId: `add_to_cart_api_v1_cart__post`

#### Status `201`
- Description: Successful Response
```json
{
  "quantity": 0,
  "book_id": 0,
  "user_id": 0,
  "id": 0,
  "create_at": "2026-01-01",
  "update_at": "2026-01-01"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/cart/summary`

### `GET /api/v1/cart/summary`
- Summary: Get My Cart Summary
- OperationId: `get_my_cart_summary_api_v1_cart_summary_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "id": 0,
    "quantity": 0,
    "book_id": 0,
    "title": "string",
    "price": 0,
    "original_price": 0,
    "image_url": "string",
    "stock_quantity": 0
  }
]
```

## `/api/v1/cart/{cart_id}`

### `DELETE /api/v1/cart/{cart_id}`
- Summary: Remove From Cart
- OperationId: `remove_from_cart_api_v1_cart__cart_id__delete`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/cart/{cart_id}`
- Summary: Update Cart Item
- OperationId: `update_cart_item_api_v1_cart__cart_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "quantity": 0,
  "book_id": 0,
  "user_id": 0,
  "id": 0,
  "create_at": "2026-01-01",
  "update_at": "2026-01-01"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/categories/`

### `GET /api/v1/categories/`
- Summary: List Categories
- OperationId: `list_categories_api_v1_categories__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "name": "string",
    "parent_id": 0,
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/categories/`
- Summary: Create Category
- OperationId: `create_category_api_v1_categories__post`

#### Status `201`
- Description: Successful Response
```json
{
  "name": "string",
  "parent_id": 0,
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/categories/roots`

### `GET /api/v1/categories/roots`
- Summary: List Root Categories
- OperationId: `list_root_categories_api_v1_categories_roots_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "name": "string",
    "parent_id": 0,
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z"
  }
]
```

## `/api/v1/categories/{category_id}`

### `GET /api/v1/categories/{category_id}`
- Summary: Get Category
- OperationId: `get_category_api_v1_categories__category_id__get`

#### Status `200`
- Description: Successful Response
```json
{
  "name": "string",
  "parent_id": 0,
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/categories/{category_id}`
- Summary: Update Category
- OperationId: `update_category_api_v1_categories__category_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "name": "string",
  "parent_id": 0,
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/favorites/`

### `GET /api/v1/favorites/`
- Summary: List My Favorites
- OperationId: `list_my_favorites_api_v1_favorites__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "author": "string",
    "code": "string",
    "edition": 0,
    "publication_date": "2026-01-01",
    "selling_price": 0,
    "stock_quantity": 0,
    "title": "string",
    "book_detail_id": 0,
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "images": [
      {
        "image_url": "string",
        "sort_order": 0,
        "is_primary": false,
        "alt_text": "string",
        "id": 0,
        "book_id": 0
      }
    ],
    "original_price": 0,
    "discount_amount": 0,
    "discount_percent": 0,
    "has_discount": false,
    "final_price": 0,
    "image_url": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/favorites/check`

### `GET /api/v1/favorites/check`
- Summary: Check Favorites
- OperationId: `check_favorites_api_v1_favorites_check_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/favorites/{book_id}`

### `DELETE /api/v1/favorites/{book_id}`
- Summary: Remove Favorite
- OperationId: `remove_favorite_api_v1_favorites__book_id__delete`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/favorites/{book_id}`
- Summary: Add Favorite
- OperationId: `add_favorite_api_v1_favorites__book_id__post`

#### Status `201`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/notifications/`

### `GET /api/v1/notifications/`
- Summary: List Notifications
- OperationId: `list_notifications_api_v1_notifications__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "message": "string",
    "title": "string",
    "type": "string",
    "id": 0,
    "send_date": "2026-01-01T00:00:00Z",
    "deleted_at": "2026-01-01T00:00:00Z"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/notifications/`
- Summary: Create Notification
- OperationId: `create_notification_api_v1_notifications__post`

#### Status `201`
- Description: Successful Response
```json
{
  "message": "string",
  "title": "string",
  "type": "string",
  "id": 0,
  "send_date": "2026-01-01T00:00:00Z",
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/notifications/broadcast`

### `POST /api/v1/notifications/broadcast`
- Summary: Broadcast Notification
- OperationId: `broadcast_notification_api_v1_notifications_broadcast_post`

#### Status `201`
- Description: Successful Response
```json
{
  "message": "string",
  "title": "string",
  "type": "string",
  "id": 0,
  "send_date": "2026-01-01T00:00:00Z",
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/notifications/me`

### `GET /api/v1/notifications/me`
- Summary: Get My Notifications
- OperationId: `get_my_notifications_api_v1_notifications_me_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/notifications/me/read-all`

### `POST /api/v1/notifications/me/read-all`
- Summary: Mark All My Notifications Read
- OperationId: `mark_all_my_notifications_read_api_v1_notifications_me_read_all_post`

#### Status `200`
- Description: Successful Response
```json
"any"
```

## `/api/v1/notifications/me/unread-count`

### `GET /api/v1/notifications/me/unread-count`
- Summary: Get My Unread Count
- OperationId: `get_my_unread_count_api_v1_notifications_me_unread_count_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

## `/api/v1/notifications/{notification_id}/read`

### `POST /api/v1/notifications/{notification_id}/read`
- Summary: Mark Notification Read
- OperationId: `mark_notification_read_api_v1_notifications__notification_id__read_post`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/`

### `GET /api/v1/orders/`
- Summary: Get My Orders
- OperationId: `get_my_orders_api_v1_orders__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "note": "string",
    "phone_number": "string",
    "shipping_address": "string",
    "payment_id": 0,
    "service_id": 0,
    "id": 0,
    "full_name": "string",
    "order_date": "2026-01-01T00:00:00Z",
    "status": "string",
    "total_price": 0,
    "user_id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "tracking_number": "string",
    "shipping_provider": "string",
    "order_items": [
      {
        "book_id": 0,
        "quantity": 0,
        "price": 0,
        "id": 0,
        "book_title": "string",
        "image_url": "string",
        "order_id": 0,
        "deleted_at": "2026-01-01T00:00:00Z"
      }
    ],
    "status_history": [
      {
        "id": 0,
        "status": "string",
        "status_change_date": "2026-01-01T00:00:00Z",
        "description": "string"
      }
    ]
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/orders/`
- Summary: Create Order
- OperationId: `create_order_api_v1_orders__post`

#### Status `201`
- Description: Successful Response
```json
{
  "note": "string",
  "phone_number": "string",
  "shipping_address": "string",
  "payment_id": 0,
  "service_id": 0,
  "id": 0,
  "full_name": "string",
  "order_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "total_price": 0,
  "user_id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "tracking_number": "string",
  "shipping_provider": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/admin/all`

### `GET /api/v1/orders/admin/all`
- Summary: Admin List Orders
- OperationId: `admin_list_orders_api_v1_orders_admin_all_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "note": "string",
    "phone_number": "string",
    "shipping_address": "string",
    "payment_id": 0,
    "service_id": 0,
    "id": 0,
    "full_name": "string",
    "order_date": "2026-01-01T00:00:00Z",
    "status": "string",
    "total_price": 0,
    "user_id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "tracking_number": "string",
    "shipping_provider": "string",
    "order_items": [
      {
        "book_id": 0,
        "quantity": 0,
        "price": 0,
        "id": 0,
        "book_title": "string",
        "image_url": "string",
        "order_id": 0,
        "deleted_at": "2026-01-01T00:00:00Z"
      }
    ],
    "status_history": [
      {
        "id": 0,
        "status": "string",
        "status_change_date": "2026-01-01T00:00:00Z",
        "description": "string"
      }
    ]
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/admin/export.csv`

### `GET /api/v1/orders/admin/export.csv`
- Summary: Admin Export Orders Csv
- OperationId: `admin_export_orders_csv_api_v1_orders_admin_export_csv_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/admin/revenue-timeseries`

### `GET /api/v1/orders/admin/revenue-timeseries`
- Summary: Admin Revenue Timeseries
- OperationId: `admin_revenue_timeseries_api_v1_orders_admin_revenue_timeseries_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "period": "string",
    "order_count": 0,
    "revenue": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/admin/stats`

### `GET /api/v1/orders/admin/stats`
- Summary: Admin Order Money Stats
- OperationId: `admin_order_money_stats_api_v1_orders_admin_stats_get`

#### Status `200`
- Description: Successful Response
```json
{
  "pending_confirm": {
    "count": 0,
    "total": 0
  },
  "shipping": {
    "count": 0,
    "total": 0
  },
  "delivered": {
    "count": 0,
    "total": 0
  },
  "cancelled": {
    "count": 0,
    "total": 0
  },
  "total_spent": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/admin/{order_id}`

### `GET /api/v1/orders/admin/{order_id}`
- Summary: Admin Get Order
- OperationId: `admin_get_order_api_v1_orders_admin__order_id__get`

#### Status `200`
- Description: Successful Response
```json
{
  "note": "string",
  "phone_number": "string",
  "shipping_address": "string",
  "payment_id": 0,
  "service_id": 0,
  "id": 0,
  "full_name": "string",
  "order_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "total_price": 0,
  "user_id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "tracking_number": "string",
  "shipping_provider": "string",
  "order_items": [
    {
      "book_id": 0,
      "quantity": 0,
      "price": 0,
      "id": 0,
      "book_title": "string",
      "image_url": "string",
      "order_id": 0,
      "deleted_at": "2026-01-01T00:00:00Z"
    }
  ],
  "status_history": [
    {
      "id": 0,
      "status": "string",
      "status_change_date": "2026-01-01T00:00:00Z",
      "description": "string"
    }
  ]
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/admin/{order_id}/cancel-decision`

### `POST /api/v1/orders/admin/{order_id}/cancel-decision`
- Summary: Admin Cancel Decision
- OperationId: `admin_cancel_decision_api_v1_orders_admin__order_id__cancel_decision_post`

#### Status `200`
- Description: Successful Response
```json
{
  "note": "string",
  "phone_number": "string",
  "shipping_address": "string",
  "payment_id": 0,
  "service_id": 0,
  "id": 0,
  "full_name": "string",
  "order_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "total_price": 0,
  "user_id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "tracking_number": "string",
  "shipping_provider": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/admin/{order_id}/shipment`

### `PATCH /api/v1/orders/admin/{order_id}/shipment`
- Summary: Admin Update Order Shipment
- OperationId: `admin_update_order_shipment_api_v1_orders_admin__order_id__shipment_patch`

#### Status `200`
- Description: Successful Response
```json
{
  "note": "string",
  "phone_number": "string",
  "shipping_address": "string",
  "payment_id": 0,
  "service_id": 0,
  "id": 0,
  "full_name": "string",
  "order_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "total_price": 0,
  "user_id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "tracking_number": "string",
  "shipping_provider": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/admin/{order_id}/status`

### `PATCH /api/v1/orders/admin/{order_id}/status`
- Summary: Admin Update Order Status
- OperationId: `admin_update_order_status_api_v1_orders_admin__order_id__status_patch`

#### Status `200`
- Description: Successful Response
```json
{
  "note": "string",
  "phone_number": "string",
  "shipping_address": "string",
  "payment_id": 0,
  "service_id": 0,
  "id": 0,
  "full_name": "string",
  "order_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "total_price": 0,
  "user_id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "tracking_number": "string",
  "shipping_provider": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/checkout`

### `POST /api/v1/orders/checkout`
- Summary: Checkout From Cart
- OperationId: `checkout_from_cart_api_v1_orders_checkout_post`

#### Status `201`
- Description: Successful Response
```json
{
  "order": {
    "note": "string",
    "phone_number": "string",
    "shipping_address": "string",
    "payment_id": 0,
    "service_id": 0,
    "id": 0,
    "full_name": "string",
    "order_date": "2026-01-01T00:00:00Z",
    "status": "string",
    "total_price": 0,
    "user_id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "tracking_number": "string",
    "shipping_provider": "string",
    "order_items": [
      {
        "book_id": 0,
        "quantity": 0,
        "price": 0,
        "id": 0,
        "book_title": "string",
        "image_url": "string",
        "order_id": 0,
        "deleted_at": "2026-01-01T00:00:00Z"
      }
    ],
    "status_history": [
      {
        "id": 0,
        "status": "string",
        "status_change_date": "2026-01-01T00:00:00Z",
        "description": "string"
      }
    ]
  },
  "item_amount": 0,
  "discount_total": 0,
  "shipping_fee": 0,
  "total_amount": 0,
  "loyalty_points_redeemed": 0,
  "points_discount_amount": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/me/stats`

### `GET /api/v1/orders/me/stats`
- Summary: Get My Order Money Stats
- OperationId: `get_my_order_money_stats_api_v1_orders_me_stats_get`

#### Status `200`
- Description: Successful Response
```json
{
  "pending_confirm": {
    "count": 0,
    "total": 0
  },
  "shipping": {
    "count": 0,
    "total": 0
  },
  "delivered": {
    "count": 0,
    "total": 0
  },
  "cancelled": {
    "count": 0,
    "total": 0
  },
  "total_spent": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/{order_id}`

### `GET /api/v1/orders/{order_id}`
- Summary: Get Order
- OperationId: `get_order_api_v1_orders__order_id__get`

#### Status `200`
- Description: Successful Response
```json
{
  "note": "string",
  "phone_number": "string",
  "shipping_address": "string",
  "payment_id": 0,
  "service_id": 0,
  "id": 0,
  "full_name": "string",
  "order_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "total_price": 0,
  "user_id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "tracking_number": "string",
  "shipping_provider": "string",
  "order_items": [
    {
      "book_id": 0,
      "quantity": 0,
      "price": 0,
      "id": 0,
      "book_title": "string",
      "image_url": "string",
      "order_id": 0,
      "deleted_at": "2026-01-01T00:00:00Z"
    }
  ],
  "status_history": [
    {
      "id": 0,
      "status": "string",
      "status_change_date": "2026-01-01T00:00:00Z",
      "description": "string"
    }
  ]
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/orders/{order_id}/cancel`

### `POST /api/v1/orders/{order_id}/cancel`
- Summary: Cancel Order
- OperationId: `cancel_order_api_v1_orders__order_id__cancel_post`

#### Status `200`
- Description: Successful Response
```json
{
  "note": "string",
  "phone_number": "string",
  "shipping_address": "string",
  "payment_id": 0,
  "service_id": 0,
  "id": 0,
  "full_name": "string",
  "order_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "total_price": 0,
  "user_id": 0,
  "deleted_at": "2026-01-01T00:00:00Z",
  "tracking_number": "string",
  "shipping_provider": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/points/admin/rewards`

### `GET /api/v1/points/admin/rewards`
- Summary: Admin List Point Rewards
- OperationId: `admin_list_point_rewards_api_v1_points_admin_rewards_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "id": 0,
    "name": "string",
    "cost_points": 0,
    "discount_percent": 0,
    "max_discount": 0,
    "valid_days": 0,
    "active": false,
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/points/admin/rewards`
- Summary: Admin Create Point Reward
- OperationId: `admin_create_point_reward_api_v1_points_admin_rewards_post`

#### Status `201`
- Description: Successful Response
```json
{
  "id": 0,
  "name": "string",
  "cost_points": 0,
  "discount_percent": 0,
  "max_discount": 0,
  "valid_days": 0,
  "active": false,
  "created_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/points/admin/rewards/{reward_id}`

### `PATCH /api/v1/points/admin/rewards/{reward_id}`
- Summary: Admin Update Point Reward
- OperationId: `admin_update_point_reward_api_v1_points_admin_rewards__reward_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "id": 0,
  "name": "string",
  "cost_points": 0,
  "discount_percent": 0,
  "max_discount": 0,
  "valid_days": 0,
  "active": false,
  "created_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/points/rewards`

### `GET /api/v1/points/rewards`
- Summary: List Point Rewards
- OperationId: `list_point_rewards_api_v1_points_rewards_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "id": 0,
    "name": "string",
    "cost_points": 0,
    "discount_percent": 0,
    "max_discount": 0,
    "valid_days": 0,
    "active": false,
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

## `/api/v1/points/rewards/{reward_id}/redeem`

### `POST /api/v1/points/rewards/{reward_id}/redeem`
- Summary: Redeem Point Reward
- OperationId: `redeem_point_reward_api_v1_points_rewards__reward_id__redeem_post`

#### Status `200`
- Description: Successful Response
```json
{
  "promotion_id": 0,
  "code": "string",
  "name": "string",
  "discount_percent": 0,
  "max_discount": 0,
  "end_date": "2026-01-01T00:00:00Z",
  "points_balance_after": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/promotions/`

### `GET /api/v1/promotions/`
- Summary: List Promotions
- OperationId: `list_promotions_api_v1_promotions__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "owner_user_id": 0,
    "code": "string",
    "name": "string",
    "discount_percent": 0,
    "max_discount": 0,
    "start_date": "2026-01-01T00:00:00Z",
    "end_date": "2026-01-01T00:00:00Z",
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/promotions/`
- Summary: Create Promotion
- OperationId: `create_promotion_api_v1_promotions__post`

#### Status `201`
- Description: Successful Response
```json
{
  "owner_user_id": 0,
  "code": "string",
  "name": "string",
  "discount_percent": 0,
  "max_discount": 0,
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-01T00:00:00Z",
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/promotions/admin/issue`

### `POST /api/v1/promotions/admin/issue`
- Summary: Admin Issue Promotion To User
- OperationId: `admin_issue_promotion_to_user_api_v1_promotions_admin_issue_post`

#### Status `201`
- Description: Successful Response
```json
{
  "owner_user_id": 0,
  "code": "string",
  "name": "string",
  "discount_percent": 0,
  "max_discount": 0,
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-01T00:00:00Z",
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/promotions/validate`

### `GET /api/v1/promotions/validate`
- Summary: Validate Promotion
- OperationId: `validate_promotion_api_v1_promotions_validate_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/promotions/{promo_id}`

### `DELETE /api/v1/promotions/{promo_id}`
- Summary: Soft Delete Promotion
- OperationId: `soft_delete_promotion_api_v1_promotions__promo_id__delete`

#### Status `200`
- Description: Successful Response
```json
{
  "owner_user_id": 0,
  "code": "string",
  "name": "string",
  "discount_percent": 0,
  "max_discount": 0,
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-01T00:00:00Z",
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/promotions/{promo_id}`
- Summary: Update Promotion
- OperationId: `update_promotion_api_v1_promotions__promo_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "owner_user_id": 0,
  "code": "string",
  "name": "string",
  "discount_percent": 0,
  "max_discount": 0,
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-01T00:00:00Z",
  "id": 0,
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/promotions/{promo_id}/stats`

### `GET /api/v1/promotions/{promo_id}/stats`
- Summary: Promotion Usage Stats
- OperationId: `promotion_usage_stats_api_v1_promotions__promo_id__stats_get`

#### Status `200`
- Description: Successful Response
```json
{
  "promotion_id": 0,
  "usage_count": 0,
  "total_discount": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/return-requests/`

### `GET /api/v1/return-requests/`
- Summary: Get My Return Requests
- OperationId: `get_my_return_requests_api_v1_return_requests__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "quantity": 0,
    "reason": "string",
    "id": 0,
    "order_id": 0,
    "order_item_id": 0,
    "request_date": "2026-01-01T00:00:00Z",
    "processed_date": "2026-01-01T00:00:00Z",
    "status": "string",
    "processed_by": 0
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/return-requests/`
- Summary: Create Return Request
- OperationId: `create_return_request_api_v1_return_requests__post`

#### Status `201`
- Description: Successful Response
```json
{
  "quantity": 0,
  "reason": "string",
  "id": 0,
  "order_id": 0,
  "order_item_id": 0,
  "request_date": "2026-01-01T00:00:00Z",
  "processed_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "processed_by": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/return-requests/admin/all`

### `GET /api/v1/return-requests/admin/all`
- Summary: Admin List Return Requests
- OperationId: `admin_list_return_requests_api_v1_return_requests_admin_all_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "quantity": 0,
    "reason": "string",
    "id": 0,
    "order_id": 0,
    "order_item_id": 0,
    "request_date": "2026-01-01T00:00:00Z",
    "processed_date": "2026-01-01T00:00:00Z",
    "status": "string",
    "processed_by": 0,
    "buyer_email": "string",
    "buyer_full_name": "string",
    "book_title": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/return-requests/{req_id}/process`

### `PATCH /api/v1/return-requests/{req_id}/process`
- Summary: Process Return Request
- OperationId: `process_return_request_api_v1_return_requests__req_id__process_patch`

#### Status `200`
- Description: Successful Response
```json
{
  "quantity": 0,
  "reason": "string",
  "id": 0,
  "order_id": 0,
  "order_item_id": 0,
  "request_date": "2026-01-01T00:00:00Z",
  "processed_date": "2026-01-01T00:00:00Z",
  "status": "string",
  "processed_by": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/reviews/`

### `POST /api/v1/reviews/`
- Summary: Create Review
- OperationId: `create_review_api_v1_reviews__post`

#### Status `201`
- Description: Successful Response
```json
{
  "content": "string",
  "rate": 0,
  "id": 0,
  "book_id": 0,
  "user_id": 0,
  "create_at": "2026-01-01T00:00:00Z",
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/reviews/admin/all`

### `GET /api/v1/reviews/admin/all`
- Summary: Admin List Reviews
- OperationId: `admin_list_reviews_api_v1_reviews_admin_all_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "content": "string",
    "rate": 0,
    "id": 0,
    "book_id": 0,
    "user_id": 0,
    "create_at": "2026-01-01T00:00:00Z",
    "deleted_at": "2026-01-01T00:00:00Z",
    "user": {
      "id": 0,
      "full_name": "string",
      "username": "string"
    }
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/reviews/admin/{review_id}`

### `DELETE /api/v1/reviews/admin/{review_id}`
- Summary: Admin Delete Review
- OperationId: `admin_delete_review_api_v1_reviews_admin__review_id__delete`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/reviews/book/{book_id}`

### `GET /api/v1/reviews/book/{book_id}`
- Summary: List Reviews By Book
- OperationId: `list_reviews_by_book_api_v1_reviews_book__book_id__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "content": "string",
    "rate": 0,
    "id": 0,
    "book_id": 0,
    "user_id": 0,
    "create_at": "2026-01-01T00:00:00Z",
    "deleted_at": "2026-01-01T00:00:00Z",
    "user": {
      "id": 0,
      "full_name": "string",
      "username": "string"
    }
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/reviews/book/{book_id}/avg`

### `GET /api/v1/reviews/book/{book_id}/avg`
- Summary: Get Book Avg Rate
- OperationId: `get_book_avg_rate_api_v1_reviews_book__book_id__avg_get`

#### Status `200`
- Description: Successful Response
```json
{
  "book_id": 0,
  "avg_rate": 0,
  "total_reviews": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/reviews/me/by-book/{book_id}`

### `GET /api/v1/reviews/me/by-book/{book_id}`
- Summary: Get My Review By Book
- OperationId: `get_my_review_by_book_api_v1_reviews_me_by_book__book_id__get`

#### Status `200`
- Description: Successful Response
```json
{
  "content": "string",
  "rate": 0,
  "id": 0,
  "book_id": 0,
  "user_id": 0,
  "create_at": "2026-01-01T00:00:00Z",
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/reviews/me/eligible`

### `GET /api/v1/reviews/me/eligible`
- Summary: Get My Review Eligibility
- OperationId: `get_my_review_eligibility_api_v1_reviews_me_eligible_get`

#### Status `200`
- Description: Successful Response
```json
{
  "eligible": false,
  "already_reviewed": false,
  "last_delivered_at": "2026-01-01T00:00:00Z",
  "reward_points_on_submit": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/reviews/{review_id}`

### `DELETE /api/v1/reviews/{review_id}`
- Summary: Delete Review
- OperationId: `delete_review_api_v1_reviews__review_id__delete`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/reviews/{review_id}`
- Summary: Update Review
- OperationId: `update_review_api_v1_reviews__review_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "content": "string",
  "rate": 0,
  "id": 0,
  "book_id": 0,
  "user_id": 0,
  "create_at": "2026-01-01T00:00:00Z",
  "deleted_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/support-requests/`

### `GET /api/v1/support-requests/`
- Summary: List Support Requests
- OperationId: `list_support_requests_api_v1_support_requests__get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "email": "string",
    "issue": "string",
    "description": "string",
    "type": "string",
    "id": 0,
    "created_at": "2026-01-01T00:00:00Z",
    "resolved_at": "2026-01-01T00:00:00Z",
    "staff_id": 0,
    "staff_name": "string",
    "staff_response": "string",
    "status": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `POST /api/v1/support-requests/`
- Summary: Create Support Request
- OperationId: `create_support_request_api_v1_support_requests__post`

#### Status `201`
- Description: Successful Response
```json
{
  "email": "string",
  "issue": "string",
  "description": "string",
  "type": "string",
  "id": 0,
  "created_at": "2026-01-01T00:00:00Z",
  "resolved_at": "2026-01-01T00:00:00Z",
  "staff_id": 0,
  "staff_name": "string",
  "staff_response": "string",
  "status": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/support-requests/{req_id}`

### `PATCH /api/v1/support-requests/{req_id}`
- Summary: Update Support Request
- OperationId: `update_support_request_api_v1_support_requests__req_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "email": "string",
  "issue": "string",
  "description": "string",
  "type": "string",
  "id": 0,
  "created_at": "2026-01-01T00:00:00Z",
  "resolved_at": "2026-01-01T00:00:00Z",
  "staff_id": 0,
  "staff_name": "string",
  "staff_response": "string",
  "status": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/support-requests/{req_id}/status`

### `PATCH /api/v1/support-requests/{req_id}/status`
- Summary: Patch Support Request Status
- OperationId: `patch_support_request_status_api_v1_support_requests__req_id__status_patch`

#### Status `200`
- Description: Successful Response
```json
{
  "email": "string",
  "issue": "string",
  "description": "string",
  "type": "string",
  "id": 0,
  "created_at": "2026-01-01T00:00:00Z",
  "resolved_at": "2026-01-01T00:00:00Z",
  "staff_id": 0,
  "staff_name": "string",
  "staff_response": "string",
  "status": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/upload/avatar`

### `POST /api/v1/upload/avatar`
- Summary: Upload Avatar
- OperationId: `upload_avatar_api_v1_upload_avatar_post`

#### Status `200`
- Description: Successful Response
```json
{
  "url": "string",
  "avatar_url": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/upload/book-detail/{detail_id}/image`

### `POST /api/v1/upload/book-detail/{detail_id}/image`
- Summary: Upload Book Detail Image
- OperationId: `upload_book_detail_image_api_v1_upload_book_detail__detail_id__image_post`

#### Status `200`
- Description: Successful Response
```json
{
  "url": "string",
  "image_url": "string",
  "detail_id": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/upload/image`

### `POST /api/v1/upload/image`
- Summary: Upload Image Endpoint
- OperationId: `upload_image_endpoint_api_v1_upload_image_post`

#### Status `200`
- Description: Successful Response
```json
{
  "url": "string"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/admin/all`

### `GET /api/v1/users/admin/all`
- Summary: Admin List Users
- OperationId: `admin_list_users_api_v1_users_admin_all_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "email": "user@example.com",
    "username": "string",
    "full_name": "string",
    "address": "string",
    "province": "string",
    "ward": "string",
    "avatar_url": "string",
    "date_of_birth": "2026-01-01T00:00:00Z",
    "gender": "string",
    "phone_number": "string",
    "id": 0,
    "is_active": false,
    "is_superuser": false,
    "loyalty_points": 0,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/admin/export.csv`

### `GET /api/v1/users/admin/export.csv`
- Summary: Admin Export Users Csv
- OperationId: `admin_export_users_csv_api_v1_users_admin_export_csv_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

## `/api/v1/users/admin/{user_id}/orders`

### `GET /api/v1/users/admin/{user_id}/orders`
- Summary: Admin List User Orders
- OperationId: `admin_list_user_orders_api_v1_users_admin__user_id__orders_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "note": "string",
    "phone_number": "string",
    "shipping_address": "string",
    "payment_id": 0,
    "service_id": 0,
    "id": 0,
    "full_name": "string",
    "order_date": "2026-01-01T00:00:00Z",
    "status": "string",
    "total_price": 0,
    "user_id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "tracking_number": "string",
    "shipping_provider": "string",
    "order_items": [
      {
        "book_id": 0,
        "quantity": 0,
        "price": 0,
        "id": 0,
        "book_title": "string",
        "image_url": "string",
        "order_id": 0,
        "deleted_at": "2026-01-01T00:00:00Z"
      }
    ],
    "status_history": [
      {
        "id": 0,
        "status": "string",
        "status_change_date": "2026-01-01T00:00:00Z",
        "description": "string"
      }
    ]
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/admin/{user_id}/points-adjust`

### `POST /api/v1/users/admin/{user_id}/points-adjust`
- Summary: Admin Adjust User Points
- OperationId: `admin_adjust_user_points_api_v1_users_admin__user_id__points_adjust_post`

#### Status `200`
- Description: Successful Response
```json
{
  "balance": 0
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/admin/{user_id}/role`

### `PATCH /api/v1/users/admin/{user_id}/role`
- Summary: Admin Set User Role
- OperationId: `admin_set_user_role_api_v1_users_admin__user_id__role_patch`

#### Status `200`
- Description: Successful Response
```json
{
  "email": "user@example.com",
  "username": "string",
  "full_name": "string",
  "address": "string",
  "province": "string",
  "ward": "string",
  "avatar_url": "string",
  "date_of_birth": "2026-01-01T00:00:00Z",
  "gender": "string",
  "phone_number": "string",
  "id": 0,
  "is_active": false,
  "is_superuser": false,
  "loyalty_points": 0,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/admin/{user_id}/status`

### `PATCH /api/v1/users/admin/{user_id}/status`
- Summary: Admin Set User Active
- OperationId: `admin_set_user_active_api_v1_users_admin__user_id__status_patch`

#### Status `200`
- Description: Successful Response
```json
{
  "email": "user@example.com",
  "username": "string",
  "full_name": "string",
  "address": "string",
  "province": "string",
  "ward": "string",
  "avatar_url": "string",
  "date_of_birth": "2026-01-01T00:00:00Z",
  "gender": "string",
  "phone_number": "string",
  "id": 0,
  "is_active": false,
  "is_superuser": false,
  "loyalty_points": 0,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/me`

### `GET /api/v1/users/me`
- Summary: Read Current User
- OperationId: `read_current_user_api_v1_users_me_get`

#### Status `200`
- Description: Successful Response
```json
{
  "email": "user@example.com",
  "username": "string",
  "full_name": "string",
  "address": "string",
  "province": "string",
  "ward": "string",
  "avatar_url": "string",
  "date_of_birth": "2026-01-01T00:00:00Z",
  "gender": "string",
  "phone_number": "string",
  "id": 0,
  "is_active": false,
  "is_superuser": false,
  "loyalty_points": 0,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

## `/api/v1/users/me/point-transactions`

### `GET /api/v1/users/me/point-transactions`
- Summary: Read My Point Transactions
- OperationId: `read_my_point_transactions_api_v1_users_me_point_transactions_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "id": 0,
    "user_id": 0,
    "delta": 0,
    "reason": "string",
    "ref_type": "string",
    "ref_id": 0,
    "balance_after": 0,
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/me/points`

### `GET /api/v1/users/me/points`
- Summary: Read My Loyalty Points
- OperationId: `read_my_loyalty_points_api_v1_users_me_points_get`

#### Status `200`
- Description: Successful Response
```json
{
  "balance": 0
}
```

## `/api/v1/users/me/promotions`

### `GET /api/v1/users/me/promotions`
- Summary: Read My Owned Promotions
- OperationId: `read_my_owned_promotions_api_v1_users_me_promotions_get`

#### Status `200`
- Description: Successful Response
```json
[
  {}
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/me/viewed`

### `GET /api/v1/users/me/viewed`
- Summary: Read My Recently Viewed
- OperationId: `read_my_recently_viewed_api_v1_users_me_viewed_get`

#### Status `200`
- Description: Successful Response
```json
[
  {
    "author": "string",
    "code": "string",
    "edition": 0,
    "publication_date": "2026-01-01",
    "selling_price": 0,
    "stock_quantity": 0,
    "title": "string",
    "book_detail_id": 0,
    "id": 0,
    "deleted_at": "2026-01-01T00:00:00Z",
    "images": [
      {
        "image_url": "string",
        "sort_order": 0,
        "is_primary": false,
        "alt_text": "string",
        "id": 0,
        "book_id": 0
      }
    ],
    "original_price": 0,
    "discount_amount": 0,
    "discount_percent": 0,
    "has_discount": false,
    "final_price": 0,
    "image_url": "string"
  }
]
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/api/v1/users/{user_id}`

### `DELETE /api/v1/users/{user_id}`
- Summary: Delete User
- OperationId: `delete_user_api_v1_users__user_id__delete`

#### Status `204`
- Description: Successful Response
```json
null
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `GET /api/v1/users/{user_id}`
- Summary: Read User
- OperationId: `read_user_api_v1_users__user_id__get`

#### Status `200`
- Description: Successful Response
```json
{
  "email": "user@example.com",
  "username": "string",
  "full_name": "string",
  "address": "string",
  "province": "string",
  "ward": "string",
  "avatar_url": "string",
  "date_of_birth": "2026-01-01T00:00:00Z",
  "gender": "string",
  "phone_number": "string",
  "id": 0,
  "is_active": false,
  "is_superuser": false,
  "loyalty_points": 0,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

### `PATCH /api/v1/users/{user_id}`
- Summary: Update User
- OperationId: `update_user_api_v1_users__user_id__patch`

#### Status `200`
- Description: Successful Response
```json
{
  "email": "user@example.com",
  "username": "string",
  "full_name": "string",
  "address": "string",
  "province": "string",
  "ward": "string",
  "avatar_url": "string",
  "date_of_birth": "2026-01-01T00:00:00Z",
  "gender": "string",
  "phone_number": "string",
  "id": 0,
  "is_active": false,
  "is_superuser": false,
  "loyalty_points": 0,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

#### Status `422`
- Description: Validation Error
```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string",
      "input": "any",
      "ctx": {}
    }
  ]
}
```

## `/kaithhealthcheck`

### `GET /kaithhealthcheck`
- Summary: Kaith Healthcheck
- OperationId: `kaith_healthcheck_kaithhealthcheck_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

## `/kaithheathcheck`

### `GET /kaithheathcheck`
- Summary: Kaith Healthcheck
- OperationId: `kaith_healthcheck_kaithheathcheck_get`

#### Status `200`
- Description: Successful Response
```json
"any"
```

