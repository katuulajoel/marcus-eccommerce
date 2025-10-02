-- This script refreshes all materialized views and ensures they contain data

-- Force a refresh of all materialized views
REFRESH MATERIALIZED VIEW bestsellingpreconfiguredproduct;
REFRESH MATERIALIZED VIEW toppreconfiguredproductspercategory;

-- If the bestsellingpreconfiguredproduct view is empty, populate it with the first product
DO $$
DECLARE
    product_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO product_count FROM bestsellingpreconfiguredproduct;

    IF product_count = 0 THEN
        -- Get the first available product if no orders exist
        WITH first_product AS (
            SELECT id, name FROM preconfiguredproduct ORDER BY id LIMIT 1
        )
        INSERT INTO bestsellingpreconfiguredproduct (preconfigured_product_id, name, times_ordered)
        SELECT id, name, 0 FROM first_product;
    END IF;
END $$;

-- If the toppreconfiguredproductspercategory view is empty, populate it with data
DO $$
DECLARE
    product_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO product_count FROM toppreconfiguredproductspercategory;

    IF product_count = 0 THEN
        -- Insert products from each category if no order data exists
        INSERT INTO toppreconfiguredproductspercategory (category_id, preconfigured_product_id, preconfigured_name, times_ordered)
        SELECT
            pp.category_id,
            pp.id AS preconfigured_product_id,
            pp.name AS preconfigured_name,
            0 AS times_ordered
        FROM preconfiguredproduct pp
        ORDER BY pp.category_id, pp.id;
    END IF;
END $$;
