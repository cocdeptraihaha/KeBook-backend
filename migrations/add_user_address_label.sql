-- Migration: add label to existing user address book table

ALTER TABLE `user_addresses`
    ADD COLUMN `label` VARCHAR(255) DEFAULT NULL AFTER `user_id`;
