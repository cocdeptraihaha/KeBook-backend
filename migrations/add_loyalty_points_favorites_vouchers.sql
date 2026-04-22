-- KeBook: loyalty points, favorites, views, point rewards, promotion owner
-- Run manually against your DB after backup. SQLite vs MySQL differ slightly.

-- === SQLite ===
-- ALTER TABLE users ADD COLUMN loyalty_points INTEGER NOT NULL DEFAULT 0;
-- (Ignore error if column already exists)

-- CREATE TABLE IF NOT EXISTS point_transactions (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   user_id INTEGER NOT NULL REFERENCES users(id),
--   delta INTEGER NOT NULL,
--   reason VARCHAR(64) NOT NULL,
--   ref_type VARCHAR(64),
--   ref_id INTEGER,
--   balance_after INTEGER NOT NULL,
--   created_at DATETIME NOT NULL
-- );
-- CREATE INDEX IF NOT EXISTS ix_point_transactions_user ON point_transactions(user_id);

-- CREATE TABLE IF NOT EXISTS favorites (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   user_id INTEGER NOT NULL REFERENCES users(id),
--   book_id INTEGER NOT NULL REFERENCES books(id),
--   created_at DATETIME NOT NULL,
--   UNIQUE(user_id, book_id)
-- );

-- CREATE TABLE IF NOT EXISTS book_views (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   user_id INTEGER NOT NULL REFERENCES users(id),
--   book_id INTEGER NOT NULL REFERENCES books(id),
--   viewed_at DATETIME NOT NULL
-- );
-- CREATE INDEX IF NOT EXISTS ix_book_views_user_viewed ON book_views(user_id, viewed_at);

-- CREATE TABLE IF NOT EXISTS point_rewards (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   name VARCHAR(255) NOT NULL,
--   cost_points INTEGER NOT NULL,
--   discount_percent REAL NOT NULL,
--   max_discount REAL,
--   valid_days INTEGER NOT NULL DEFAULT 30,
--   active INTEGER NOT NULL DEFAULT 1,
--   created_at DATETIME NOT NULL
-- );

-- ALTER TABLE promotion ADD COLUMN owner_user_id INTEGER REFERENCES users(id);
-- (SQLite 3.35+: ignore if exists)

-- === MySQL ===
ALTER TABLE users ADD COLUMN loyalty_points INT NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS point_transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  delta INT NOT NULL,
  reason VARCHAR(64) NOT NULL,
  ref_type VARCHAR(64) NULL,
  ref_id INT NULL,
  balance_after INT NOT NULL,
  created_at DATETIME NOT NULL,
  INDEX ix_point_transactions_user (user_id),
  CONSTRAINT fk_pt_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS favorites (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  book_id INT NOT NULL,
  created_at DATETIME NOT NULL,
  UNIQUE KEY uq_favorite_user_book (user_id, book_id),
  INDEX ix_favorites_user (user_id),
  CONSTRAINT fk_fav_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_fav_book FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE IF NOT EXISTS book_views (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  book_id INT NOT NULL,
  viewed_at DATETIME NOT NULL,
  INDEX ix_book_views_user_viewed (user_id, viewed_at),
  CONSTRAINT fk_bv_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_bv_book FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE IF NOT EXISTS point_rewards (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  cost_points INT NOT NULL,
  discount_percent DOUBLE NOT NULL,
  max_discount DOUBLE NULL,
  valid_days INT NOT NULL DEFAULT 30,
  active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL
);

ALTER TABLE promotion ADD COLUMN owner_user_id INT NULL,
  ADD INDEX ix_promotion_owner (owner_user_id),
  ADD CONSTRAINT fk_promo_owner FOREIGN KEY (owner_user_id) REFERENCES users(id);
