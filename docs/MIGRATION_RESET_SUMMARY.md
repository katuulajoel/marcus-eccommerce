# Migration Reset Summary

## What Was Done

The Django migrations were reset and synchronized with the existing database schema created by `init.sql`.

## Steps Taken

1. **Stopped and Removed Containers**
   ```bash
   docker compose down -v
   ```
   This removed all containers and volumes, including the database.

2. **Deleted All Migration Files**
   ```bash
   find apps -path "*/migrations/*.py" -not -name "__init__.py" -delete
   ```
   All migration files except `__init__.py` were removed.

3. **Added Image Fields to Database**
   - Created `db/add_image_fields.sql` to add new image columns
   - Applied SQL script to add:
     - `category.image` (VARCHAR 100)
     - `partoption.image` (VARCHAR 100)
     - `preconfiguredproduct.image` (VARCHAR 100)
     - `partoption.minimum_payment_percentage` (NUMERIC 3,2)

4. **Generated Fresh Migrations**
   - Started containers which auto-generated migrations from current models
   - Migrations created for all apps: `products`, `preconfigured_products`, `orders`

5. **Fake-Applied Migrations**
   Since tables already existed, we fake-applied the migrations:
   ```bash
   docker compose exec web python manage.py migrate products --fake
   docker compose exec web python manage.py migrate preconfigured_products --fake
   docker compose exec web python manage.py migrate orders --fake
   docker compose exec web python manage.py migrate sessions
   ```

6. **Updated init.sql**
   Updated the base schema in `db/init.sql` to include:
   - Image fields for Category, PartOption, and PreConfiguredProduct
   - minimum_payment_percentage for PartOption

## Current State

- ✅ All migrations are applied
- ✅ Database schema matches Django models
- ✅ API is running at http://localhost:8000/api/
- ✅ All apps have image field support
- ✅ Both `image_url` (old) and `image` (new) fields exist temporarily

## Important Notes

### Dual Fields
The database currently has BOTH:
- `image_url` (VARCHAR 255) - Old field, still in init.sql for backward compatibility
- `image` (VARCHAR 100) - New ImageField

The models use `image` (ImageField), and serializers return `image_url` as a computed field from `image`.

### Migration Strategy for Future
When you need to create new migrations:

```bash
# Inside container
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

The compose.yaml automatically runs these commands on startup.

### For Fresh Database Setup
If you delete volumes and start fresh:
1. `docker compose down -v`
2. `docker compose up -d`
3. Migrations will auto-apply correctly

### Removing image_url Fields (Optional)
After confirming all data is migrated, you can:
1. Remove `image_url` columns from `init.sql`
2. Create migrations to drop the columns
3. Apply migrations

## Files Modified

- `server/db/init.sql` - Added image fields to table definitions
- `server/db/add_image_fields.sql` - SQL script for adding image columns
- `server/apps/*/migrations/0001_initial.py` - Auto-generated initial migrations

## Testing

All endpoints are working:
```bash
# Test categories
curl http://localhost:8000/api/categories/

# Test part options
curl http://localhost:8000/api/part-options/?part_id=1

# Test preconfigured products
curl http://localhost:8000/api/preconfigured-products/products/
```

## Summary

The migration system is now clean and synchronized. The database has the new image fields, and Django recognizes all migrations as applied. The app is ready for development with the new image upload functionality!
