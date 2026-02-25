-- Thêm SEPAY vào enum payment method
USE `kebookdb`;

ALTER TABLE `payment`
  MODIFY COLUMN `method` enum('BANK_TRANSFER','CASH','COD','CREDIT_CARD','VNPAY','SEPAY') DEFAULT NULL;
