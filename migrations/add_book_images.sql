-- Add multi-image support for books.
-- MySQL 8+

CREATE TABLE IF NOT EXISTS book_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_primary TINYINT(1) NOT NULL DEFAULT 0,
    alt_text VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_book_images_book_sort (book_id, sort_order),
    INDEX idx_book_images_book_primary (book_id, is_primary),
    CONSTRAINT fk_book_images_book
        FOREIGN KEY (book_id) REFERENCES books(id)
        ON DELETE CASCADE
);

-- Backfill from existing single-image field.
INSERT INTO book_images (book_id, image_url, sort_order, is_primary, alt_text)
SELECT b.id, bd.image_url, 0, 1, NULL
FROM books b
JOIN book_details bd ON bd.id = b.book_detail_id
WHERE bd.image_url IS NOT NULL
  AND bd.image_url <> ''
  AND NOT EXISTS (
      SELECT 1 FROM book_images bi
      WHERE bi.book_id = b.id
  );

-- Ensure exactly one primary per book where images exist.
UPDATE book_images bi
JOIN (
    SELECT book_id, MIN(id) AS min_id
    FROM book_images
    GROUP BY book_id
) x ON x.book_id = bi.book_id
SET bi.is_primary = CASE WHEN bi.id = x.min_id THEN 1 ELSE 0 END
WHERE NOT EXISTS (
    SELECT 1
    FROM book_images b2
    WHERE b2.book_id = bi.book_id AND b2.is_primary = 1
);
