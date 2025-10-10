import os
import django
import sys

# Initialize Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

# Get admin credentials from environment variables
ADMIN_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
ADMIN_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
ADMIN_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

# Create superuser if not exists
try:
    if not User.objects.filter(username=ADMIN_USERNAME).exists():
        print(f'Creating superuser {ADMIN_USERNAME}...')
        User.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
        print('Superuser created successfully!')
    else:
        print('Superuser already exists.')
except IntegrityError:
    print('Superuser already exists.')
except Exception as e:
    print(f'Error creating superuser: {str(e)}')
