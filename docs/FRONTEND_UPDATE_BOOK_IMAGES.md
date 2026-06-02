# Frontend Update Guide: Multi Images per Book

## 1) Summary
- Backend now supports multiple images per book via `book_images`.
- Old field `book_detail.image_url` is still kept for backward compatibility.
- Frontend should migrate to `images[]` for gallery/thumbnail/primary logic.

## 2) Data Contract Changes

## Book response (`GET /api/v1/books/{book_id}`)
- Old:
  - `image_url` (single URL, computed)
- New:
  - `images`: array of image objects
  - `image_url` still exists as fallback (primary image if available)

Example:
```json
{
  "id": 12,
  "title": "Book A",
  "image_url": "https://.../primary.jpg",
  "images": [
    {
      "id": 101,
      "book_id": 12,
      "image_url": "https://.../primary.jpg",
      "sort_order": 0,
      "is_primary": true,
      "alt_text": "Front cover"
    },
    {
      "id": 102,
      "book_id": 12,
      "image_url": "https://.../back.jpg",
      "sort_order": 1,
      "is_primary": false,
      "alt_text": "Back cover"
    }
  ]
}
```

## 3) New Endpoints for Images

Base: `/api/v1/books/{book_id}/images`

1. `GET /api/v1/books/{book_id}/images`
- Auth: Public
- Purpose: list all images of book sorted by `sort_order`, then `id`.

2. `POST /api/v1/books/{book_id}/images`
- Auth: Admin
- Body:
```json
{
  "image_url": "https://.../new.jpg",
  "sort_order": 2,
  "is_primary": false,
  "alt_text": "Side view"
}
```
- Notes:
  - If `is_primary=true`, backend will clear old primary.
  - Backend guarantees max one primary per book.
  - Legacy `book_detail.image_url` auto-sync with current primary.

3. `PATCH /api/v1/books/{book_id}/images/{image_id}`
- Auth: Admin
- Body (partial):
```json
{
  "sort_order": 0,
  "is_primary": true
}
```
- Notes:
  - Supports partial update.
  - Setting `is_primary=true` moves primary role to this image.

4. `DELETE /api/v1/books/{book_id}/images/{image_id}`
- Auth: Admin
- Response: `204 No Content`
- Notes:
  - After delete, backend re-ensures one primary if images remain.
  - Legacy `book_detail.image_url` auto-sync again.

## 4) Frontend Migration Plan

1. Display logic
- Product card/list:
  - Prefer `book.image_url` (already computed by backend).
- Product detail gallery:
  - Use `book.images` as source of thumbnails + slider.
  - Primary image:
    - `images.find(x => x.is_primary)` first
    - fallback `images[0]`
    - fallback `book.image_url`

2. Admin edit page
- Add image manager section:
  - Upload/add image URL
  - Reorder by `sort_order`
  - Set primary
  - Delete image
- Save actions call image endpoints above.

3. State handling
- Query keys:
  - `book-detail:{id}`
  - `book-images:{id}`
- Invalidate both keys after create/update/delete image.

## 5) Error Handling
- `404 Book not found`:
  - show not-found toast/page.
- `404 Book image not found`:
  - refresh image list and notify user.
- `401/403` on admin actions:
  - redirect login or show permission denied.

## 6) Backward Compatibility Window
- During transition:
  - Old screens may still read `book_detail.image_url`.
  - New screens should use `images[]`.
- Recommendation:
  - Move all product detail/gallery UI to `images[]` first.
  - Keep old fallback until all clients updated.

## 7) QA Checklist
- Product detail shows multiple thumbnails.
- Changing primary in admin updates main image on public page.
- Deleting primary image auto-selects new primary.
- Sorting images changes thumbnail order correctly.
- Old pages still show image via `image_url` fallback.

