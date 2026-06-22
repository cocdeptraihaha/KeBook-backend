-- Migration: Add image support and refund fields to ReturnRequest
-- Supporting both SQLite and MySQL compatibilities

ALTER TABLE `return_requests` ADD COLUMN `image_url` VARCHAR(1024) DEFAULT NULL;
ALTER TABLE `return_requests` ADD COLUMN `refund_amount` DECIMAL(12, 2) DEFAULT 0.00;
