-- Setup automatic refresh for materialized views using pg_cron

DO $$
BEGIN
    -- Enable the pg_cron extension if available
    BEGIN
        -- Step 1: Enable the pg_cron extension
        CREATE EXTENSION IF NOT EXISTS pg_cron;
        
        -- Step 2: Grant usage to the database user
        GRANT USAGE ON SCHEMA cron TO ecommerce_user;
        
        -- Step 3: Create unique indexes for both materialized views
                CREATE UNIQUE INDEX IF NOT EXISTS idx_top_preconfigured_unique 
        ON TopPreconfiguredProductsPerCategory (category_id, preconfigured_product_id);
        
        CREATE UNIQUE INDEX IF NOT EXISTS idx_best_selling_unique
        ON BestSellingPreconfiguredProduct (preconfigured_product_id);
        
        -- Step 4: Schedule automatic refreshes using different dollar quote delimiters
                PERFORM cron.schedule(
          'refresh_top_preconfigured_products',
          '0 */6 * * *',
          'REFRESH MATERIALIZED VIEW CONCURRENTLY TopPreconfiguredProductsPerCategory'
        );
        
        PERFORM cron.schedule(
          'refresh_best_selling_preconfigured',
          '5 */6 * * *',
          'REFRESH MATERIALIZED VIEW CONCURRENTLY BestSellingPreconfiguredProduct'
        );
        
        RAISE NOTICE 'Successfully set up pg_cron for materialized view refreshes';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Could not set up pg_cron: % - continuing without automatic refreshes', SQLERRM;
    END;
END;
$$;

-- Create the indexes anyway, even if pg_cron isn't available
CREATE UNIQUE INDEX IF NOT EXISTS idx_top_preconfigured_unique 
ON TopPreconfiguredProductsPerCategory (category_id, preconfigured_product_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_best_selling_unique
ON BestSellingPreconfiguredProduct (preconfigured_product_id);
