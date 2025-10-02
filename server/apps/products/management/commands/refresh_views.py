from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Refresh materialized views after data changes'

    def handle(self, *args, **options):
        self.stdout.write('Refreshing materialized views...')

        with connection.cursor() as cursor:
            try:
                cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY bestsellingpreconfiguredproduct;")
                cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY toppreconfiguredproductspercategory;")
                self.stdout.write(self.style.SUCCESS('✅ Successfully refreshed materialized views!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error refreshing views: {str(e)}'))
                raise
