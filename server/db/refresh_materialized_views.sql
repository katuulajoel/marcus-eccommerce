-- This script refreshes all materialized views and ensures they contain data

-- Force a refresh of all materialized views
REFRESH MATERIALIZED VIEW BestSellingPreconfiguredProduct;
REFRESH MATERIALIZED VIEW TopPreconfiguredProductsPerCategory;

-- If the BestSellingPreconfiguredProduct view is empty, populate it with the first product
DO $$
DECLARE
    product_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO product_count FROM BestSellingPreconfiguredProduct;
    
    IF product_count = 0 THEN
        -- Get the first available product if no orders exist
        WITH first_product AS (
            SELECT id, name FROM PreconfiguredProduct ORDER BY id LIMIT 1
        )
        INSERT INTO BestSellingPreconfiguredProduct (preconfigured_product_id, name, times_ordered)
        SELECT id, name, 0 FROM first_product;
    END IF;
END $$;

-- If the TopPreconfiguredProductsPerCategory view is empty, populate it with data
DO $$
DECLARE
    product_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO product_count FROM TopPreconfiguredProductsPerCategory;
    
    IF product_count = 0 THEN
        -- Insert products from each category if no order data exists
        INSERT INTO TopPreconfiguredProductsPerCategory (id, category_id, product_name, price, times_ordered, preconfigured_product_id)
        SELECT 
            ROW_NUMBER() OVER (ORDER BY pp.category_id, pp.id) as id,
            pp.category_id,
            pp.name AS product_name,
            pp.base_price AS price,
            0 AS times_ordered,
            pp.id AS preconfigured_product_id
        FROM PreconfiguredProduct pp
        ORDER BY pp.category_id, pp.id;
    END IF;
END $$;
