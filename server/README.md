# Marcus E-commerce Backend

A Django-based e-commerce backend with REST API support for products, orders, customers, and product configuration.

## Prerequisites

- Docker
- Docker Compose

## Setup and Running

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

## API Documentation

You can access the Swagger API documentation at:
- Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/api/swagger/)

## Default Superuser Credentials

The default superuser credentials are as follows (set in the `docker-compose` environment variables):

- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: `admin123`

You can change these credentials by updating the following environment variables in the `docker-compose` file:

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

## API Endpoints

- Categories API: `/api/categories/`
- Orders API: `/api/orders/`
- Customers API: `/api/customers/`
- Configurator API: `/api/configurator/`
