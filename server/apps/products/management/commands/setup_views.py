from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Setup materialized views indexes and pg_cron refresh schedule'

    def handle(self, *args, **options):
        self.stdout.write('Setting up materialized views...')

        with connection.cursor() as cursor:
            try:
                # Create unique indexes for concurrent refresh
                self.stdout.write('Creating unique indexes...')
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_top_preconfigured_unique
                    ON toppreconfiguredproductspercategory (category_id, preconfigured_product_id);
                """)
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_best_selling_unique
                    ON bestsellingpreconfiguredproduct (preconfigured_product_id);
                """)
                self.stdout.write(self.style.SUCCESS('✓ Created unique indexes'))

                # Refresh views initially (this will populate them from the query)
                self.stdout.write('Refreshing materialized views...')
                cursor.execute("REFRESH MATERIALIZED VIEW bestsellingpreconfiguredproduct;")
                cursor.execute("REFRESH MATERIALIZED VIEW toppreconfiguredproductspercategory;")
                self.stdout.write(self.style.SUCCESS('✓ Refreshed materialized views (they will be populated after seed data is loaded)'))

                # Setup pg_cron
                self.stdout.write('Setting up pg_cron...')
                cursor.execute("""
                    DO $$
                    BEGIN
                        BEGIN
                            CREATE EXTENSION IF NOT EXISTS pg_cron;
                            GRANT USAGE ON SCHEMA cron TO ecommerce_user;

                            -- Schedule refreshes
                            PERFORM cron.schedule(
                              'refresh_top_preconfigured_products',
                              '0 */6 * * *',
                              'REFRESH MATERIALIZED VIEW CONCURRENTLY toppreconfiguredproductspercategory'
                            );

                            PERFORM cron.schedule(
                              'refresh_best_selling_preconfigured',
                              '5 */6 * * *',
                              'REFRESH MATERIALIZED VIEW CONCURRENTLY bestsellingpreconfiguredproduct'
                            );

                            RAISE NOTICE 'Successfully set up pg_cron for materialized view refreshes';
                        EXCEPTION
                            WHEN OTHERS THEN
                                RAISE NOTICE 'Could not set up pg_cron: % - continuing without automatic refreshes', SQLERRM;
                        END;
                    END;
                    $$;
                """)
                self.stdout.write(self.style.SUCCESS('✓ Setup pg_cron scheduled refreshes'))

                self.stdout.write(self.style.SUCCESS('\n✅ Successfully setup materialized views!'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error setting up views: {str(e)}'))
                raise
