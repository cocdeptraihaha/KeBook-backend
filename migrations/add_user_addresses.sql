-- Migration: add user address book support

CREATE TABLE IF NOT EXISTS `user_addresses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `label` VARCHAR(255) DEFAULT NULL,
    `recipient_name` VARCHAR(255) DEFAULT NULL,
    `phone_number` VARCHAR(255) DEFAULT NULL,
    `address_detail` VARCHAR(255) DEFAULT NULL,
    `ward` VARCHAR(255) DEFAULT NULL,
    `province` VARCHAR(255) DEFAULT NULL,
    `is_default` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME DEFAULT NULL,
    CONSTRAINT `fk_user_addresses_user`
        FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_addresses_user` (`user_id`),
    INDEX `idx_user_addresses_default` (`user_id`, `is_default`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `orders`
    ADD COLUMN `address_id` INT NULL AFTER `user_id`;

ALTER TABLE `orders`
    ADD CONSTRAINT `fk_orders_address`
    FOREIGN KEY (`address_id`) REFERENCES `user_addresses`(`id`) ON DELETE SET NULL;

INSERT INTO `user_addresses` (
    `user_id`,
    `label`,
    `recipient_name`,
    `phone_number`,
    `address_detail`,
    `ward`,
    `province`,
    `is_default`,
    `created_at`,
    `updated_at`
)
SELECT
    u.`id`,
    NULL,
    u.`full_name`,
    u.`phone_number`,
    u.`address`,
    u.`ward`,
    u.`province`,
    TRUE,
    COALESCE(u.`created_at`, CURRENT_TIMESTAMP),
    COALESCE(u.`updated_at`, CURRENT_TIMESTAMP)
FROM `users` u
WHERE
    u.`deleted_at` IS NULL
    AND (
        NULLIF(TRIM(COALESCE(u.`full_name`, '')), '') IS NOT NULL
        OR NULLIF(TRIM(COALESCE(u.`phone_number`, '')), '') IS NOT NULL
        OR NULLIF(TRIM(COALESCE(u.`address`, '')), '') IS NOT NULL
        OR NULLIF(TRIM(COALESCE(u.`ward`, '')), '') IS NOT NULL
        OR NULLIF(TRIM(COALESCE(u.`province`, '')), '') IS NOT NULL
    )
    AND NOT EXISTS (
        SELECT 1
        FROM `user_addresses` ua
        WHERE ua.`user_id` = u.`id`
          AND ua.`deleted_at` IS NULL
    );
