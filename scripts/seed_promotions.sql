-- Seed demo promotion codes for checkout
-- Run in MySQL:  SOURCE scripts/seed_promotions.sql;

USE kebookdb;

INSERT INTO promotion (code, name, discount_percent, max_discount, start_date, end_date, deleted_at)
VALUES
  -- NEWUSER10: giảm 10%, tối đa 50k
  ('NEWUSER10', 'New user 10% off', 10, 50000, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), NULL),

  -- FREESHIP: giảm 100% tối đa 30k (thường dùng để bù phí ship mặc định)
  ('FREESHIP', 'Free shipping up to 30k', 100, 30000, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), NULL),

  -- BIGSALE50: giảm 50k, tối đa 50k
  ('BIGSALE50', 'Big sale 50k off', NULL, 50000, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), NULL);

