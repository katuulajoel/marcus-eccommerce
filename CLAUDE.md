# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Marcus Custom Bikes is an e-commerce platform for selling customizable bikes (and other products like surfboards and skis). Customers can select different components (frame, handlebars, wheels, etc.) to create their perfect bike with real-time price updates and compatibility validation.

**Tech Stack:**
- Frontend: React + TypeScript + Vite + Tailwind CSS
- Backend: Django + Django REST Framework + PostgreSQL
- Monorepo structure with separate client and admin apps

## Development Commands

### Backend (Django)

```bash
# Navigate to server directory
cd server

# Start all services (PostgreSQL + Django)
docker compose up --build -d

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser (default: admin/admin123)
docker compose exec web python manage.py createsuperuser

# Stop services
docker compose stop

# Stop and remove containers
docker compose down
```

- API available at: http://localhost:8000/api/
- Admin interface: http://localhost:8000/admin/
- Swagger docs: http://localhost:8000/api/swagger/

### Frontend (React)

```bash
# Install dependencies (from project root)
npm install

# Run client app (customer-facing store)
npm run dev:client
# Client runs at http://localhost:3000

# Run admin app (admin dashboard)
npm run dev:admin
# Admin runs at http://localhost:3001

# Build for production
npm run build              # Build both apps
npm run build:client       # Client only
npm run build:admin        # Admin only
```

## Architecture

### Backend Structure

Django apps are located in `server/apps/`:
- **products**: Categories, Parts, PartOptions, PriceAdjustmentRule, IncompatibilityRule, Stock
- **preconfigured_products**: Base product models with default configurations
- **configurator**: API for product configuration logic
- **orders**: Order and OrderItem management
- **customers**: Customer data management

**Key API Endpoints:**
- `/api/categories/` - Product categories and parts
- `/api/preconfigured-products/` - Pre-configured product models
- `/api/configurator/` - Product configuration logic
- `/api/orders/` - Order management
- `/api/customers/` - Customer management

### Frontend Structure

Located in `web/`:
- **client/**: Customer-facing store (port 3000)
  - Pages: Home, CategoryPage, CustomizePage, CartPage
  - Key hooks: `use-product-configuration.ts`, `use-product-rules.ts`, `use-product-stock.ts`
  - Context: `cart-context.tsx` (localStorage-based cart)
- **admin/**: Admin dashboard (port 3001) - UI not yet connected to backend
- **shared/**: Shared components, hooks, and utilities

**Import Aliases:**
- `@shared` → `web/shared`
- `@client` → `web/client`
- `@admin` → `web/admin`

### Data Model Key Concepts

1. **Product Customization Flow:**
   - Customer selects a Category (Bikes, Surfboards, Skis)
   - Chooses a PreconfiguredProduct as starting point (or builds from scratch)
   - Customizes Parts (Frame, Wheels, etc.) by selecting PartOptions
   - System validates compatibility via IncompatibilityRule
   - Price is calculated using default_price + PriceAdjustmentRule conditions
   - Stock availability checked via Stock table

2. **Price Calculation:**
   - Each PartOption has a `default_price`
   - PriceAdjustmentRule can modify price when specific combinations are selected
   - Hook `use-product-rules.ts` handles price calculation logic

3. **Product Configuration:**
   - PreconfiguredProduct has base configuration in PreconfiguredProductParts
   - Customers can modify any part while maintaining compatibility
   - Admin can use similar configurator to create/edit preconfigured products

4. **Materialized Views (Analytics):**
   - `TopPreconfiguredProductsPerCategory` - Top sellers per category
   - `BestSellingPreconfiguredProduct` - Overall best seller
   - Auto-refreshed every 6 hours via pg_cron

### Current Implementation Status

**Working:**
- Product browsing and category pages
- Product customization with real-time pricing
- Compatibility validation
- Stock availability checking
- Cart (localStorage-based)
- Backend API fully functional

**In Progress:**
- Admin UI connection to backend (currently uses mock data)
- Checkout process to create backend orders
- Cart migration from localStorage to backend

## Important Development Notes

### Frontend Environment

Create `web/.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000/
```

### Database Schema

The PostgreSQL database has extensive indexing on:
- Foreign keys (customer_id, category_id, part_id, etc.)
- Combination indexes for PriceAdjustmentRule and IncompatibilityRule lookups

Refer to `/docs/marcus_ecommerce_erd.jpeg` for full ERD diagram.

### Cart Implementation

Current cart is client-side only (localStorage). When implementing checkout:
1. POST cart items to `/api/orders/` to create Order
2. Create OrderProduct entries with selected PreconfiguredProduct
3. Create OrderItem entries for each part option with final_price
4. Clear localStorage cart after successful order creation

### Admin Portal Configuration

The admin portal includes a BikeCustomizer-style configurator for creating/editing PreconfiguredProducts. This provides:
- Visual part selection interface
- Real-time price calculation
- Compatibility validation
- Stock availability checking
