-- Thêm SEPAY vào enum payment method
USE `kebookdb`;

ALTER TABLE `payment`
  MODIFY COLUMN `method` enum('COD','SEPAY') DEFAULT NULL;
