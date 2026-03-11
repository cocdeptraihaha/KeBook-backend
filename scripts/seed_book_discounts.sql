-- Seed active book discounts for demo/testing
-- Assumes books with these IDs exist. Adjust IDs as needed.

USE `kebookdb`;

-- Clear existing demo links (optional)
DELETE FROM book_book_discount WHERE book_id IN (51, 52, 54, 55, 60, 61, 62, 63, 64, 65);

-- Optionally remove old demo discounts (they will no longer be linked)
-- DELETE FROM book_discounts WHERE id IN (...);

-- Active discounts (start_date <= now <= end_date)
INSERT INTO book_discounts (discount_amount, discount_percent, end_date, start_date) VALUES
  (NULL, 10, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 30 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY)),   -- d1
  (15000, NULL, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 7 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY)),  -- d2
  (NULL, 20, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 3 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY)),     -- d3
  (NULL, 5,  DATE_ADD(UTC_TIMESTAMP(), INTERVAL 14 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY)),    -- d4
  (30000, NULL, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 5 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY));  -- d5

-- Link discounts to books (many-to-many). Adjust book IDs as needed.
-- Assume books with IDs 51,52,54,55,60,61,62,63,64,65 exist.

SET @d1_id := (SELECT MIN(id) FROM book_discounts WHERE discount_percent = 10);
SET @d2_id := (SELECT MIN(id) FROM book_discounts WHERE discount_amount = 15000);
SET @d3_id := (SELECT MIN(id) FROM book_discounts WHERE discount_percent = 20);
SET @d4_id := (SELECT MIN(id) FROM book_discounts WHERE discount_percent = 5);
SET @d5_id := (SELECT MIN(id) FROM book_discounts WHERE discount_amount = 30000);

INSERT INTO book_book_discount (book_id, discount_id) VALUES
  (51, @d1_id),
  (52, @d2_id),
  (54, @d3_id),
  (55, @d4_id),
  (60, @d5_id),
  (61, @d1_id),
  (62, @d2_id),
  (63, @d3_id),
  (64, @d4_id),
  (65, @d5_id);


