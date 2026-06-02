-- Migration: upgrade rewards and promotions for fixed discount, free shipping, and limits

ALTER TABLE `point_rewards`
    ADD COLUMN `description` VARCHAR(500) NULL AFTER `name`,
    ADD COLUMN `reward_type` VARCHAR(32) NOT NULL DEFAULT 'DISCOUNT_PERCENT' AFTER `description`,
    ADD COLUMN `icon` VARCHAR(64) NULL AFTER `reward_type`,
    ADD COLUMN `discount_amount` DOUBLE NULL AFTER `discount_percent`,
    ADD COLUMN `min_order_amount` DOUBLE NULL AFTER `max_discount`,
    ADD COLUMN `usage_limit` INT NULL AFTER `min_order_amount`,
    ADD COLUMN `used_count` INT NOT NULL DEFAULT 0 AFTER `usage_limit`;

ALTER TABLE `promotion`
    ADD COLUMN `discount_amount` DOUBLE NULL AFTER `discount_percent`,
    ADD COLUMN `free_shipping` TINYINT(1) NOT NULL DEFAULT 0 AFTER `discount_amount`;

SET @OLD_SQL_SAFE_UPDATES = @@SQL_SAFE_UPDATES;
SET SQL_SAFE_UPDATES = 0;

UPDATE `point_rewards`
SET `reward_type` = 'DISCOUNT_PERCENT'
WHERE `reward_type` IS NULL OR `reward_type` = '';

SET SQL_SAFE_UPDATES = @OLD_SQL_SAFE_UPDATES;
