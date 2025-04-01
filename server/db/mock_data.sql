-- Mock data for e-commerce database

BEGIN;

-- Customers
INSERT INTO customer (id, name, email, phone) VALUES
(1, 'Alice Johnson', 'alice.j@example.com', '+256701234567'),
(2, 'Bob Smith', 'bob.smith@example.com', '+256712345678');

-- Reset the customer sequence to continue from the last inserted ID
SELECT setval('customer_id_seq', (SELECT MAX(id) FROM customer));

-- Categories (renamed from Products)
INSERT INTO category (id, name, description) VALUES
(1, 'Bicycles', 'A wide range of customizable bicycles designed for various terrains and purposes. Includes options for mountain biking, city commuting, and road cycling.');

-- Reset the category sequence
SELECT setval('category_id_seq', (SELECT MAX(id) FROM category));

-- Parts
INSERT INTO part (id, name, category_id, step) VALUES
(1, 'Frame', 1, 1),
(2, 'Finish', 1, 2),
(3, 'Wheels', 1, 3),
(4, 'Rims', 1, 4),
(5, 'Chain', 1, 5);

-- Reset the part sequence
SELECT setval('part_id_seq', (SELECT MAX(id) FROM part));

-- Part Options
INSERT INTO partoption (id, part_id, name, default_price, image_url, description) VALUES
(1, 1, 'Full-Suspension Frame', 130.00, 'http://localhost:8000/media/images/partoption/full_frame_suspension.jpg', 'A durable and lightweight frame designed for rugged mountain trails. Provides excellent shock absorption and stability.'),
(2, 1, 'Diamond Frame', 100.00, 'http://localhost:8000/media/images/partoption/frame_diamond.jpg', 'A classic frame design known for its strength and simplicity. Ideal for city and road biking.'),
(3, 2, 'Matte Finish', 50.00, 'http://localhost:8000/media/images/partoption/finish_matte.jpg', 'A sleek and modern matte finish that resists scratches and fingerprints. Perfect for a stylish look.'),
(4, 2, 'Shiny Finish', 30.00, 'http://localhost:8000/media/images/partoption/finish_shiny.jpg', 'A glossy finish that enhances the bike’s appearance with a reflective shine. Easy to clean and maintain.'),
(5, 3, 'Mountain Wheels', 90.00, 'http://localhost:8000/media/images/partoption/wheels_mountain.jpg', 'Sturdy wheels designed for off-road biking. Provides excellent grip and durability on uneven terrain.'),
(6, 3, 'Road Wheels', 80.00, 'http://localhost:8000/media/images/partoption/wheels_road.jpg', 'Lightweight wheels optimized for speed and efficiency on paved roads. Ideal for long-distance rides.'),
(7, 4, 'red', 20.00, 'http://localhost:8000/media/images/partoption/red_rims.jpg', 'Vibrant red rims that add a bold and sporty look to your bike. Made from high-quality materials for durability.'),
(8, 4, 'white', 20.00, 'http://localhost:8000/media/images/partoption/white_rims.jpg', 'Elegant white rims that complement any bike design. Provides a clean and modern aesthetic.'),
(9, 5, '8-Speed Chain', 45.00, 'http://localhost:8000/media/images/partoption/chain_8_speed.jpg', 'A high-performance chain designed for smooth and reliable shifting across 8-speed gears.'),
(10, 5, 'Single-Speed Chain', 40.00, 'http://localhost:8000/media/images/partoption/chain_single_speed.jpg', 'A durable chain built for single-speed bikes. Offers low maintenance and long-lasting performance.');

-- Reset the partoption sequence
SELECT setval('partoption_id_seq', (SELECT MAX(id) FROM partoption));

-- Preconfigured Products
INSERT INTO preconfiguredproduct (id, category_id, name, base_price, image_url, description) VALUES
(1, 1, 'Mountain Bike', 450.00, 'http://localhost:8000/media/images/preconfigured/mountain_bike.jpg', 'A rugged mountain bike equipped with top-quality components for off-road adventures. Designed for durability and performance on challenging trails.'),
(2, 1, 'City Bike', 300.00, 'http://localhost:8000/media/images/preconfigured/city_bike.jpg', 'A versatile city bike perfect for commuting and leisure rides. Combines comfort, style, and practicality for urban environments.');

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
(2, 8, 5, 'White rims are incompatible with Mountain Wheels.');

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
