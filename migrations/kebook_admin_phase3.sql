-- Phase 3: tracking đơn, sách SEO/publish, promotion limits, audit log
-- Chạy thủ công trên MySQL khi triển khai production.

ALTER TABLE orders ADD COLUMN tracking_number VARCHAR(64) NULL;
ALTER TABLE orders ADD COLUMN shipping_provider VARCHAR(64) NULL;

ALTER TABLE books ADD COLUMN is_published TINYINT(1) NOT NULL DEFAULT 1;
ALTER TABLE books ADD COLUMN slug VARCHAR(255) NULL;
ALTER TABLE books ADD COLUMN meta_description VARCHAR(255) NULL;

ALTER TABLE promotion ADD COLUMN min_order_amount DOUBLE NULL;
ALTER TABLE promotion ADD COLUMN usage_limit INT NULL;
ALTER TABLE promotion ADD COLUMN used_count INT NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS admin_audit_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  actor_user_id INT NULL,
  action VARCHAR(128) NOT NULL,
  target_type VARCHAR(64) NULL,
  target_id INT NULL,
  payload JSON NULL,
  ip VARCHAR(64) NULL,
  created_at DATETIME NULL,
  CONSTRAINT fk_admin_audit_actor FOREIGN KEY (actor_user_id) REFERENCES users(id)
);
