# Generated manually to create materialized views

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('preconfigured_products', '0001_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Create materialized view for top preconfigured products per category
            CREATE MATERIALIZED VIEW IF NOT EXISTS toppreconfiguredproductspercategory AS
            SELECT
                pp.category_id,
                pp.id AS preconfigured_product_id,
                pp.name AS preconfigured_name,
                COUNT(op.id) AS times_ordered
            FROM preconfiguredproduct pp
            JOIN orderproduct op ON op.preconfigured_product_id = pp.id
            GROUP BY pp.category_id, pp.id, pp.name
            ORDER BY pp.category_id, times_ordered DESC;

            -- Create materialized view for best-selling preconfigured product
            CREATE MATERIALIZED VIEW IF NOT EXISTS bestsellingpreconfiguredproduct AS
            SELECT
                pp.id AS preconfigured_product_id,
                pp.name,
                COUNT(op.id) AS times_ordered
            FROM preconfiguredproduct pp
            JOIN orderproduct op ON op.preconfigured_product_id = pp.id
            GROUP BY pp.id, pp.name
            ORDER BY times_ordered DESC
            LIMIT 1;
            """,
            reverse_sql="""
            DROP MATERIALIZED VIEW IF EXISTS bestsellingpreconfiguredproduct;
            DROP MATERIALIZED VIEW IF EXISTS toppreconfiguredproductspercategory;
            """
        ),
    ]
