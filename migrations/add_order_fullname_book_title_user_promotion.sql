-- Add full_name to orders
ALTER TABLE `orders` ADD COLUMN `full_name` VARCHAR(255) DEFAULT NULL AFTER `id`;

-- Add book_title to order_items
ALTER TABLE `order_items` ADD COLUMN `book_title` VARCHAR(255) DEFAULT NULL AFTER `id`;

-- Create user_promotion table
CREATE TABLE IF NOT EXISTS `user_promotion` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `promotion_id` INT NOT NULL,
    `order_id` INT DEFAULT NULL,
    `used_at` DATETIME NOT NULL,
    CONSTRAINT `fk_user_promotion_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_promotion_promotion` FOREIGN KEY (`promotion_id`) REFERENCES `promotion`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_promotion_order` FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`) ON DELETE SET NULL,
    INDEX `idx_user_promotion_user` (`user_id`),
    INDEX `idx_user_promotion_promotion` (`promotion_id`),
    UNIQUE KEY `uq_user_promotion` (`user_id`, `promotion_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
