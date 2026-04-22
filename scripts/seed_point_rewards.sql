-- Gói đổi điểm mẫu (chạy sau khi đã tạo bảng point_rewards)
INSERT INTO point_rewards (name, cost_points, discount_percent, max_discount, valid_days, active, created_at)
SELECT 'Voucher 10% (tối đa 50.000đ)', 100, 10, 50000, 30, 1, datetime('now')
WHERE NOT EXISTS (SELECT 1 FROM point_rewards WHERE cost_points = 100 AND discount_percent = 10);

INSERT INTO point_rewards (name, cost_points, discount_percent, max_discount, valid_days, active, created_at)
SELECT 'Voucher 15% (tối đa 100.000đ)', 300, 15, 100000, 30, 1, datetime('now')
WHERE NOT EXISTS (SELECT 1 FROM point_rewards WHERE cost_points = 300 AND discount_percent = 15);
