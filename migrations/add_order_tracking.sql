-- Migration: add order tracking support
-- Run this if tables already exist (won't be needed if tables are recreated)

-- 1. Add new enum values to orders.status
ALTER TABLE orders MODIFY COLUMN status ENUM(
  'CANCELLED','CANCEL_REQUESTED','COMPLETED','CONFIRMED',
  'DELIVERED','INPROGRESS','PENDING','RETURNED','SHIPPED'
);

-- 2. Add new enum values to order_status_history.e_order_history
ALTER TABLE order_status_history MODIFY COLUMN e_order_history ENUM(
  'CANCELLED','CANCEL_REQUESTED','COMPLETED','CONFIRMED',
  'DELIVERED','INPROGRESS','PENDING','PROCESSING','RETURNED','SHIPPED'
);

-- 3. Add description column to order_status_history
ALTER TABLE order_status_history ADD COLUMN description VARCHAR(500) NULL;
