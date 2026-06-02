-- Gói đổi điểm mẫu (MySQL; chạy sau khi đã tạo bảng point_rewards)
INSERT INTO point_rewards (
  name, description, reward_type, icon, cost_points,
  discount_percent, discount_amount, max_discount, min_order_amount,
  usage_limit, used_count, valid_days, active, created_at
)
SELECT
  'Voucher giảm 50.000đ',
  'Giảm 50.000đ cho đơn hàng từ 500.000đ',
  'DISCOUNT_AMOUNT',
  'ticket-percent',
  500,
  NULL,
  50000,
  NULL,
  500000,
  1250,
  0,
  30,
  1,
  NOW()
WHERE NOT EXISTS (SELECT 1 FROM point_rewards WHERE name = 'Voucher giảm 50.000đ');

INSERT INTO point_rewards (
  name, description, reward_type, icon, cost_points,
  discount_percent, discount_amount, max_discount, min_order_amount,
  usage_limit, used_count, valid_days, active, created_at
)
SELECT
  'Voucher giảm 100.000đ',
  'Giảm 100.000đ cho đơn hàng từ 1.000.000đ',
  'DISCOUNT_AMOUNT',
  'ticket-percent',
  1000,
  NULL,
  100000,
  NULL,
  1000000,
  780,
  0,
  30,
  1,
  NOW()
WHERE NOT EXISTS (SELECT 1 FROM point_rewards WHERE name = 'Voucher giảm 100.000đ');

INSERT INTO point_rewards (
  name, description, reward_type, icon, cost_points,
  discount_percent, discount_amount, max_discount, min_order_amount,
  usage_limit, used_count, valid_days, active, created_at
)
SELECT
  'Miễn phí vận chuyển',
  'Miễn phí vận chuyển cho đơn hàng từ 300.000đ',
  'FREE_SHIPPING',
  'truck',
  300,
  NULL,
  NULL,
  NULL,
  300000,
  2000,
  0,
  30,
  1,
  NOW()
WHERE NOT EXISTS (SELECT 1 FROM point_rewards WHERE name = 'Miễn phí vận chuyển');

INSERT INTO point_rewards (
  name, description, reward_type, icon, cost_points,
  discount_percent, discount_amount, max_discount, min_order_amount,
  usage_limit, used_count, valid_days, active, created_at
)
SELECT
  'Voucher giảm 20%',
  'Giảm 20% tối đa 200.000đ cho đơn hàng từ 1.200.000đ',
  'DISCOUNT_PERCENT',
  'gift',
  1500,
  20,
  NULL,
  200000,
  1200000,
  450,
  0,
  30,
  1,
  NOW()
WHERE NOT EXISTS (SELECT 1 FROM point_rewards WHERE name = 'Voucher giảm 20%');
