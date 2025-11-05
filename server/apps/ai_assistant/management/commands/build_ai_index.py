"""
Django management command to build/rebuild the AI knowledge index.
Run this after adding new products or making database changes.

Usage:
    python manage.py build_ai_index
    python manage.py build_ai_index --rebuild  # Force full rebuild
"""

from django.core.management.base import BaseCommand
from apps.ai_assistant.services.index_service import get_index_service


class Command(BaseCommand):
    help = 'Build or rebuild the AI assistant knowledge index from database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='Force a complete rebuild of the index (deletes existing data)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting AI index build...'))

        index_service = get_index_service()

        try:
            if options['rebuild']:
                self.stdout.write(self.style.WARNING('Rebuilding index from scratch...'))
                index_service.rebuild_index()
            else:
                self.stdout.write(self.style.WARNING('Building index...'))
                index_service.build_index()

            self.stdout.write(self.style.SUCCESS('✓ AI index built successfully!'))

            # Show stats
            stats = index_service.get_stats()
            self.stdout.write(self.style.SUCCESS(f'\nIndex Statistics:'))
            for key, value in stats.items():
                self.stdout.write(f'  {key}: {value}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error building index: {str(e)}'))
            raise
