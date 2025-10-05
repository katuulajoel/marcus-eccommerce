from django.db import connection, transaction
from django.core.management.base import BaseCommand
from django.core import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import os
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Load seed data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading seed data',
        )

    def _fix_user_passwords(self):
        """Ensure seeded users have properly hashed passwords"""
        seeded_users = {
            'alice.j': 'P@ssword123',
            'bob.smith': 'P@ssword123',
        }

        for username, password in seeded_users.items():
            try:
                user = User.objects.get(username=username)
                # Check if password is properly hashed by trying to verify it
                if not user.check_password(password):
                    # Password is not properly hashed, fix it
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.WARNING(f'⚠️  Fixed password for user: {username}'))
            except User.DoesNotExist:
                pass

    def handle(self, *args, **options):
        self.stdout.write('Loading seed data...')

        try:
            # Check if data already exists (unless --clear flag is used)
            if not options['clear']:
                from apps.products.models import Category
                if Category.objects.exists():
                    # Fix user passwords in case they were improperly seeded
                    self._fix_user_passwords()
                    self.stdout.write(self.style.SUCCESS('✅ Seed data already exists. Skipping...'))
                    self.stdout.write(self.style.WARNING('Use --clear flag to reseed database'))
                    return

            # Get the absolute path to the fixture file
            fixture_path = os.path.join('/app', 'fixtures', 'seed_data.json')

            with open(fixture_path, 'r') as f:
                data = json.load(f)

            # Start transaction
            with transaction.atomic():
                # Clear existing data if --clear flag is provided
                if options['clear']:
                    from apps.customers.models import Customer
                    self.stdout.write('Clearing existing data...')
                    # Use Django ORM to delete data (respects foreign keys)
                    from apps.products.models import Category, Part, PartOption, Stock
                    from apps.preconfigured_products.models import PreConfiguredProduct
                    from apps.configurator.models import PriceAdjustmentRule, IncompatibilityRule

                    # Delete in order of dependencies
                    try:
                        from apps.orders.models import Orders
                        Orders.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        Stock.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        IncompatibilityRule.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        PriceAdjustmentRule.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        PreConfiguredProduct.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        PartOption.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        Part.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        Category.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        Customer.objects.all().delete()
                    except Exception:
                        pass
                    try:
                        User.objects.all().delete()
                    except Exception:
                        pass
                    self.stdout.write(self.style.SUCCESS('✅ Cleared existing data'))

                # Disable triggers to allow auto_now_add fields to be set
                with connection.cursor() as cursor:
                    cursor.execute("SET session_replication_role = 'replica';")

                # Separate user, customer, and other data
                user_data = []
                customer_data = []
                other_data = []

                for obj in data:
                    if obj['model'] == 'auth.user':
                        user_data.append(obj)
                    elif obj['model'] == 'customers.customer':
                        customer_data.append(obj)
                    else:
                        other_data.append(obj)

                # Create users first
                users_map = {}
                for user_obj in user_data:
                    # Handle password hashing
                    if 'password' in user_obj['fields']:
                        user_obj['fields']['password'] = make_password(user_obj['fields']['password'])
                    
                    # Create user
                    user = User(
                        id=user_obj['pk'],
                        password=user_obj['fields']['password'],
                        username=user_obj['fields']['username'],
                        email=user_obj['fields'].get('email', ''),
                        first_name=user_obj['fields'].get('first_name', ''),
                        last_name=user_obj['fields'].get('last_name', ''),
                        is_staff=user_obj['fields'].get('is_staff', False),
                        is_active=user_obj['fields'].get('is_active', True),
                        is_superuser=user_obj['fields'].get('is_superuser', False),
                        date_joined=user_obj['fields'].get('date_joined', timezone.now())
                    )
                    user.save()
                    users_map[user_obj['pk']] = user

                # Create customers, linking to users
                for customer_obj in customer_data:
                    user_id = customer_obj['fields'].get('user')
                    if not user_id:
                        self.stdout.write(self.style.WARNING(
                            f"Customer {customer_obj['pk']} has no associated user. Skipping."
                        ))
                        continue

                    # Get the user
                    user = users_map.get(user_id)
                    if not user:
                        self.stdout.write(self.style.WARNING(
                            f"User with id {user_id} not found for customer {customer_obj['pk']}. Skipping."
                        ))
                        continue

                    # Create customer
                    from apps.customers.models import Customer
                    Customer.objects.create(
                        id=customer_obj['pk'],
                        user=user,
                        name=customer_obj['fields'].get('name', ''),
                        email=user.email,  # Use email from user
                        phone=customer_obj['fields'].get('phone', ''),
                        email_verified=customer_obj['fields'].get('email_verified', False),
                        created_at=customer_obj['fields'].get('created_at', timezone.now())
                    )

                # Load all other data
                for obj in other_data:
                    try:
                        model = serializers.deserialize('json', json.dumps([obj]))
                        for m in model:
                            m.save()
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f"Error loading {obj['model']} {obj['pk']}: {str(e)}"
                        ))

                # Re-enable triggers
                with connection.cursor() as cursor:
                    cursor.execute("SET session_replication_role = 'origin';")

                # Reset sequences for all tables to prevent duplicate key errors
                with connection.cursor() as cursor:
                    # Get list of all sequences in the database
                    cursor.execute("""
                        SELECT
                            t.relname AS table_name,
                            a.attname AS column_name,
                            s.relname AS sequence_name
                        FROM pg_class AS s
                        JOIN pg_depend AS d ON d.objid = s.oid
                        JOIN pg_class AS t ON d.refobjid = t.oid
                        JOIN pg_attribute AS a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
                        JOIN pg_namespace AS n ON n.oid = s.relnamespace
                        WHERE s.relkind = 'S'
                        AND n.nspname = 'public';
                    """)
                    tables_with_sequences = cursor.fetchall()

                    for table_name, column_name, sequence_name in tables_with_sequences:
                        try:
                            # Get the max ID for this table
                            cursor.execute(f"SELECT MAX({column_name}) FROM {table_name};")
                            max_id = cursor.fetchone()[0]

                            if max_id is not None:
                                # Set sequence to max_id with is_called=true, so next value is max_id + 1
                                cursor.execute(f"""
                                    SELECT setval(pg_get_serial_sequence('{table_name}', '{column_name}'),
                                           {max_id}, true);
                                """)
                            else:
                                # No rows, set sequence to 1 with is_called=false, so next value is 1
                                cursor.execute(f"""
                                    SELECT setval(pg_get_serial_sequence('{table_name}', '{column_name}'),
                                           1, false);
                                """)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"Could not reset sequence for {table_name}.{column_name}: {str(e)}"))

                    self.stdout.write(self.style.SUCCESS('✅ Reset database sequences'))

            self.stdout.write(self.style.SUCCESS('✅ Successfully loaded seed data!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error loading seed data: {str(e)}'))
            # Make sure to re-enable triggers even if there's an error
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET session_replication_role = 'origin';")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error re-enabling triggers: {str(e)}'))
            raise  # Re-raise the exception to ensure the transaction is rolled back
