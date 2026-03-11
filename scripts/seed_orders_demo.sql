-- Seed demo orders and order_items to generate sales data for top-selling books.
-- NOTE:
-- - Adjust book_id, user_id, payment_id, service_id if they don't exist in your database.
-- - This script assumes books with IDs 51, 52, 54, 55, 60 already exist (same as seed_book_discounts.sql).
-- - Orders are marked as COMPLETED so they count as real sales.

USE `kebookdb`;

-- Optional: clear existing demo orders for these books (comment out if not desired)
-- DELETE oi FROM order_items oi
-- JOIN orders o ON o.id = oi.order_id
-- WHERE oi.book_id IN (51, 52, 54, 55, 60);
-- DELETE FROM orders WHERE note LIKE 'Demo order%';

-- Demo order 1: focus on book 51 (best seller)
INSERT INTO orders (note, order_date, phone_number, shipping_address, status, total_price, payment_id, service_id, user_id)
VALUES ('Demo order 1', DATE_SUB(UTC_TIMESTAMP(), INTERVAL 7 DAY), '0900000001', 'Demo address 1', 'COMPLETED', 5 * 120000, 1, 1, 25);
SET @order1_id := LAST_INSERT_ID();

INSERT INTO order_items (price, quantity, book_id, order_id, is_deleted, deleted_at) VALUES
  (120000, 5, 51, @order1_id, b'0', NULL);

-- Demo order 2: mix of book 51 and 52
INSERT INTO orders (note, order_date, phone_number, shipping_address, status, total_price, payment_id, service_id, user_id)
VALUES ('Demo order 2', DATE_SUB(UTC_TIMESTAMP(), INTERVAL 5 DAY), '0900000002', 'Demo address 2', 'COMPLETED', 3 * 120000 + 2 * 150000, 1, 1, 25);
SET @order2_id := LAST_INSERT_ID();

INSERT INTO order_items (price, quantity, book_id, order_id, is_deleted, deleted_at) VALUES
  (120000, 3, 51, @order2_id, b'0', NULL),
  (150000, 2, 52, @order2_id, b'0', NULL);

-- Demo order 3: books 54 and 55
INSERT INTO orders (note, order_date, phone_number, shipping_address, status, total_price, payment_id, service_id, user_id)
VALUES ('Demo order 3', DATE_SUB(UTC_TIMESTAMP(), INTERVAL 3 DAY), '0900000003', 'Demo address 3', 'COMPLETED', 1 * 90000 + 4 * 110000, 1, 1, 25);
SET @order3_id := LAST_INSERT_ID();

INSERT INTO order_items (price, quantity, book_id, order_id, is_deleted, deleted_at) VALUES
  (90000, 1, 54, @order3_id, b'0', NULL),
  (110000, 4, 55, @order3_id, b'0', NULL);

-- Demo order 4: heavy on book 60 (second best seller)
INSERT INTO orders (note, order_date, phone_number, shipping_address, status, total_price, payment_id, service_id, user_id)
VALUES ('Demo order 4', DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 DAY), '0900000004', 'Demo address 4', 'COMPLETED', 6 * 155000, 1, 1, 25);
SET @order4_id := LAST_INSERT_ID();

INSERT INTO order_items (price, quantity, book_id, order_id, is_deleted, deleted_at) VALUES
  (155000, 6, 60, @order4_id, b'0', NULL);

-- Demo order 5: small mixed order to diversify counts
INSERT INTO orders (note, order_date, phone_number, shipping_address, status, total_price, payment_id, service_id, user_id)
VALUES ('Demo order 5', UTC_TIMESTAMP(), '0900000005', 'Demo address 5', 'COMPLETED', 1 * 120000 + 1 * 150000 + 1 * 155000, 1, 1, 25);
SET @order5_id := LAST_INSERT_ID();

INSERT INTO order_items (price, quantity, book_id, order_id, is_deleted, deleted_at) VALUES
  (120000, 1, 51, @order5_id, b'0', NULL),
  (150000, 1, 52, @order5_id, b'0', NULL),
  (155000, 1, 60, @order5_id, b'0', NULL);

