-- Mock data for e-commerce database

BEGIN;

-- Customers
INSERT INTO customer (id, name, email, phone) VALUES
(1, 'Alice Johnson', 'alice.j@example.com', '+256701234567'),
(2, 'Bob Smith', 'bob.smith@example.com', '+256712345678');

-- Reset the customer sequence to continue from the last inserted ID
SELECT setval('customer_id_seq', (SELECT MAX(id) FROM customer));

-- Products
INSERT INTO product (id, name, description) VALUES
(1, 'Bicycle', 'Customizable bicycles');

-- Reset the product sequence
SELECT setval('product_id_seq', (SELECT MAX(id) FROM product));

-- Parts
INSERT INTO part (id, name, product_id) VALUES
(1, 'Frame', 1),
(2, 'Finish', 1),
(3, 'Wheels', 1),
(4, 'Rims', 1),
(5, 'Chain', 1);

-- Reset the part sequence
SELECT setval('part_id_seq', (SELECT MAX(id) FROM part));

-- Part Options
INSERT INTO partoption (id, part_id, name, default_price) VALUES
(1, 1, 'Full-Suspension Frame', 130.00),
(2, 1, 'Diamond Frame', 100.00),
(3, 2, 'Matte Finish', 50.00),
(4, 2, 'Shiny Finish', 30.00),
(5, 3, 'Mountain Wheels', 90.00),
(6, 3, 'Road Wheels', 80.00),
(7, 4, 'Black Rims', 20.00),
(8, 4, 'Blue Rims', 20.00),
(9, 5, '8-Speed Chain', 45.00),
(10, 5, 'Single-Speed Chain', 40.00);

-- Reset the partoption sequence
SELECT setval('partoption_id_seq', (SELECT MAX(id) FROM partoption));

-- Preconfigured Products
INSERT INTO preconfiguredproduct (id, product_id, name, base_price) VALUES
(1, 1, 'Mountain Bike', 450.00),
(2, 1, 'City Bike', 300.00);

-- Reset the preconfiguredproduct sequence
SELECT setval('preconfiguredproduct_id_seq', (SELECT MAX(id) FROM preconfiguredproduct));

-- Preconfigured Product Parts
INSERT INTO preconfiguredproductparts (id, preconfigured_product_id, part_option_id) VALUES
(1, 1, 1),
(2, 1, 3),
(3, 1, 5),
(4, 1, 7),
(5, 1, 9),
(6, 2, 2),
(7, 2, 4),
(8, 2, 6),
(9, 2, 8),
(10, 2, 10);

-- Reset the preconfiguredproductparts sequence
SELECT setval('preconfiguredproductparts_id_seq', (SELECT MAX(id) FROM preconfiguredproductparts));

-- Price Adjustment Rules
INSERT INTO priceadjustmentrule (id, affected_option_id, condition_option_id, adjusted_price) VALUES
(1, 3, 1, 50.00),  -- Matte Finish price adjustment for Full-Suspension Frame
(2, 3, 2, 35.00),  -- Matte Finish price adjustment for Diamond Frame
(3, 9, 6, 10.00);  -- 8-Speed Chain price adjustment for Road Wheels

-- Reset the priceadjustmentrule sequence
SELECT setval('priceadjustmentrule_id_seq', (SELECT MAX(id) FROM priceadjustmentrule));

-- Incompatibility Rules
INSERT INTO incompatibilityrule (id, part_option_id, incompatible_with_option_id, message) VALUES
(1, 5, 2, 'Mountain wheels can only be used with a Full-Suspension Frame.'),
(2, 8, 5, 'Blue rims are incompatible with Mountain Wheels.');

-- Reset the incompatibilityrule sequence
SELECT setval('incompatibilityrule_id_seq', (SELECT MAX(id) FROM incompatibilityrule));

-- Stock
INSERT INTO stock (id, part_option_id, quantity) VALUES
(1, 1, 15),
(2, 2, 20),
(3, 3, 25),
(4, 4, 30),
(5, 5, 10),
(6, 6, 20),
(7, 7, 18),
(8, 8, 12),
(9, 9, 15),
(10, 10, 20);

-- Reset the stock sequence
SELECT setval('stock_id_seq', (SELECT MAX(id) FROM stock));

-- Orders and Order Products
INSERT INTO orders (id, customer_id, total_price) VALUES
(1, 1, 335.00),
(2, 2, 490.00);

-- Reset the orders sequence
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));

INSERT INTO orderproduct (id, order_id, preconfigured_product_id, custom_name, base_product_name) VALUES
(1, 1, 2, 'City Cruiser', 'City Bike'),
(2, 2, 1, 'Trail Blazer', 'Mountain Bike');

-- Reset the orderproduct sequence
SELECT setval('orderproduct_id_seq', (SELECT MAX(id) FROM orderproduct));

-- Order Items
INSERT INTO orderitem (id, order_product_id, part_name, option_name, final_price) VALUES
(1, 1, 'Frame', 'Diamond Frame', 100.00),
(2, 1, 'Finish', 'Shiny Finish', 30.00),
(3, 1, 'Wheels', 'Road Wheels', 80.00),
(4, 1, 'Rims', 'Blue Rims', 20.00),
(5, 1, 'Chain', 'Single-Speed Chain', 40.00),
(6, 2, 'Frame', 'Full-Suspension Frame', 130.00),
(7, 2, 'Finish', 'Matte Finish', 50.00),
(8, 2, 'Wheels', 'Mountain Wheels', 90.00),
(9, 2, 'Rims', 'Black Rims', 20.00),
(10, 2, 'Chain', '8-Speed Chain', 45.00);

-- Reset the orderitem sequence
SELECT setval('orderitem_id_seq', (SELECT MAX(id) FROM orderitem));

COMMIT;
