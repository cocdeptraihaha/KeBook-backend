-- Chạy một lần trên MySQL nếu app báo: Unknown column 'users.loyalty_points'
-- (Đồng bộ với app/models/user.py)

ALTER TABLE users ADD COLUMN loyalty_points INT NOT NULL DEFAULT 0;
