from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import connection
import os
import json


class Command(BaseCommand):
    help = 'Load seed data for development'

    def handle(self, *args, **options):
        self.stdout.write('Loading seed data...')

        try:
            # Get the absolute path to the fixture file
            fixture_path = os.path.join('/app', 'fixtures', 'seed_data.json')

            with open(fixture_path, 'r') as f:
                data = json.load(f)

            # Disable triggers to allow auto_now_add fields to be set
            with connection.cursor() as cursor:
                cursor.execute("SET session_replication_role = 'replica';")

            # Load the fixtures
            for obj in serializers.deserialize('json', json.dumps(data)):
                obj.save()

            # Re-enable triggers
            with connection.cursor() as cursor:
                cursor.execute("SET session_replication_role = 'origin';")

            self.stdout.write(self.style.SUCCESS('✅ Successfully loaded seed data!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error loading seed data: {str(e)}'))
            # Make sure to re-enable triggers even if there's an error
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET session_replication_role = 'origin';")
            except:
                pass
