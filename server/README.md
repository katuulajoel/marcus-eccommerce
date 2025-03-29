# Marcus E-commerce Backend

A Django-based e-commerce backend with REST API support for products, orders, customers, and product configuration.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- RabbitMQ 3+

## Setup and Running (Using Docker)

The easiest way to get started is using Docker, which will set up all required services:

1. Navigate to the server directory:
   ```
   cd server
   ```

2. Build and start the containers:
   ```
   docker compose up --build -d
   ```

3. Run migrations:
   ```
   docker compose exec web python manage.py migrate
   ```

4. Create a superuser (optional):
   ```
   docker compose exec web python manage.py createsuperuser
   ```

5. Access the API at http://localhost:8000/api/
   Access the admin interface at http://localhost:8000/admin/

6. To stop the containers:
   ```
   docker compose stop
   ```

7. To stop and remove containers, networks, and volumes:
   ```
   docker compose down
   ```

## Setup and Running (Without Docker)

1. Set up a PostgreSQL database:
   - Create a database named `ecommerce_db`
   - Create a user `ecommerce_user` with password `ecommerce_password`
   - Grant all privileges on the database to the user

2. Install Redis and RabbitMQ.

3. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```
   cd server
   pip install -r requirements.txt
   ```

5. Update the database configuration in `ecommerce_backend/settings.py` to point to your local PostgreSQL instance.

6. Run migrations:
   ```
   python manage.py migrate
   ```

7. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

8. Start the development server:
   ```
   python manage.py runserver
   ```

9. In a separate terminal, start the Celery worker:
   ```
   celery -A ecommerce_backend worker -l info
   ```

## API Endpoints

- Products API: `/api/products/`
- Orders API: `/api/orders/`
- Customers API: `/api/customers/`
- Configurator API: `/api/configurator/`

## Development

- Run tests:
  ```
  docker-compose exec web python manage.py test
  ```
  
- Check for linting errors:
  ```
  docker-compose exec web flake8
  ```
