-- Seed active book discounts for demo/testing
-- Assumes books with these IDs exist. Adjust IDs as needed.

USE `kebookdb`;

-- Clear existing discounts for the selected demo books (optional)
DELETE FROM book_discounts WHERE book_id IN (51, 52, 54, 55, 60);

-- Active discounts (start_date <= now <= end_date)
INSERT INTO book_discounts (discount_amount, discount_percent, end_date, start_date, book_id) VALUES
  (NULL, 10, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 30 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY), 51),
  (15000, NULL, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 7 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY), 52),
  (NULL, 20, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 3 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY), 54),
  (NULL, 5,  DATE_ADD(UTC_TIMESTAMP(), INTERVAL 14 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY), 55),
  (30000, NULL, DATE_ADD(UTC_TIMESTAMP(), INTERVAL 5 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY), 60);

-- Expired discount (should NOT apply)
INSERT INTO book_discounts (discount_amount, discount_percent, end_date, start_date, book_id) VALUES
  (NULL, 50, DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY), DATE_SUB(UTC_TIMESTAMP(), INTERVAL 10 DAY), 51);

