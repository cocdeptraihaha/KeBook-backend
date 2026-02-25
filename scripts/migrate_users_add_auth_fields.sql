-- Migration: Thêm các field auth của backend vào bảng users
-- Giữ nguyên các field profile: id, address, avatar_url, date_of_birth, full_name, gender, phone_number
-- Chạy trên database bookmagasin (chạy một lần duy nhất)

USE `bookmagasin`;

-- 1. Thêm các cột auth mới vào bảng users (giữ nguyên profile)
ALTER TABLE `users`
  ADD COLUMN `email` VARCHAR(255) NULL,
  ADD COLUMN `username` VARCHAR(255) NULL,
  ADD COLUMN `hashed_password` VARCHAR(255) NULL,
  ADD COLUMN `is_active` TINYINT(1) NOT NULL DEFAULT 0,
  ADD COLUMN `is_superuser` TINYINT(1) NOT NULL DEFAULT 0,
  ADD COLUMN `created_at` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  ADD COLUMN `updated_at` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);

-- 2. Thêm unique constraint cho email và username
ALTER TABLE `users`
  ADD UNIQUE KEY `ux_users_email` (`email`),
  ADD UNIQUE KEY `ux_users_username` (`username`);

-- 3. Tạo bảng otps (nếu chưa tồn tại)
CREATE TABLE IF NOT EXISTS `otps` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `code` VARCHAR(6) NOT NULL,
  `otp_type` ENUM('activation', 'reset_password') NOT NULL,
  `is_used` TINYINT(1) NOT NULL DEFAULT 0,
  `expires_at` DATETIME(6) NOT NULL,
  `created_at` DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  KEY `idx_otps_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
