# Marcus Custom Bikes - E-commerce Platform

## Table of Contents
1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Data Model](#data-model)
4. [Main User Actions](#main-user-actions)
5. [Product Page](#product-page)
6. [Add to Cart Action](#add-to-cart-action)
7. [Administrative Workflows](#administrative-workflows)
8. [New Product Creation](#new-product-creation)
9. [Adding New Part Choices](#adding-new-part-choices)
10. [Setting Prices](#setting-prices)
11. [Installation and Setup](#installation-and-setup)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
    - [Current State of the Applications](#current-state-of-the-applications)
    - [Cart Implementation](#cart-implementation)
12. [Future Plans](#future-plans)

## Overview

This platform allows Marcus to sell customizable bikes where customers can select different components (frame, handlebars, wheels, etc.) to create their perfect bike. Each combination can have different pricing and availability.

## Tech Stack

- **Frontend**: React with TypeScript, powered by Vite for fast development
- **Backend**: Django
- **Database**: PostgreSQL
- **CSS Framework**: Tailwind CSS

## Data Model

The data model is relational to handle complex product configurations and pricing rules. You can view the Entity Relationship Diagram (ERD) here:

![Database ERD](/docs/marcus_ecommerce_erd.jpeg)

### Tables

#### Customer
```
customer
- id (PK)
- name
- email
- phone
- created_at
```

#### Orders
```
orders
- id (PK)
- customer_id (FK to customer)
- total_price
- created_at
```

#### Category
```
category
- id (PK)
- name
- description
- created_at
```

#### Part
```
part
- id (PK)
- name
- category_id (FK to category)
- step
```

#### Part Option
```
partoption
- id (PK)
- part_id (FK to part)
- name
- default_price
- image_url
- description
```

#### Preconfigured Product
```
preconfiguredproduct
- id (PK)
- category_id (FK to category)
- name
- base_price
- image_url
- description
```

#### Preconfigured Product Parts
```
preconfiguredproductparts
- id (PK)
- preconfigured_product_id (FK to preconfiguredproduct)
- part_option_id (FK to partoption)
```

#### Price Adjustment Rule
```
priceadjustmentrule
- id (PK)
- affected_option_id (FK to partoption)
- condition_option_id (FK to partoption)
- adjusted_price
```

#### Stock
```
stock
- id (PK)
- part_option_id (FK to partoption)
- quantity
```

#### Order Product
```
orderproduct
- id (PK)
- order_id (FK to orders)
- preconfigured_product_id (FK to preconfiguredproduct)
- custom_name
- base_product_name
```

#### Order Item
```
orderitem
- id (PK)
- order_product_id (FK to orderproduct)
- part_name
- option_name
- final_price
```

#### Incompatibility Rule
```
incompatibilityrule
- id (PK)
- part_option_id (FK to partoption)
- incompatible_with_option_id (FK to partoption)
- message
```

### Indexes

Indexes have been added to optimize query performance for frequently accessed columns. Key indexes include:

- **Customer**: `idx_customer_name` on the `name` column.
- **Orders**: 
  - `idx_orders_customer_id` on the `customer_id` column.
  - `idx_orders_created_at` on the `created_at` column.
- **Part**: `idx_part_category_id` on the `category_id` column.
- **PartOption**: `idx_partoption_part_id` on the `part_id` column.
- **OrderProduct**: `idx_orderproduct_order_id` on the `order_id` column.
- **PriceAdjustmentRule**: `idx_price_adjustment_combo` on the combination of `affected_option_id` and `condition_option_id`.
- **IncompatibilityRule**: `idx_incompatibility_rule` on the combination of `part_option_id` and `incompatible_with_option_id`.
- **PreconfiguredProduct**: `idx_preconfiguredproduct_category_id` on the `category_id` column.

### Materialized Views

Materialized views are used for analytics and reporting purposes. These views are refreshed periodically to provide up-to-date insights.

#### Top Preconfigured Products per Category
- **Purpose**: Displays the top-selling preconfigured products for each category.
- **Columns**:
  - `category_id`: The category of the product.
  - `preconfigured_product_id`: The ID of the preconfigured product.
  - `preconfigured_name`: The name of the preconfigured product.
  - `times_ordered`: The number of times the product has been ordered.
- **Refresh Command**:
  ```
  REFRESH MATERIALIZED VIEW TopPreconfiguredProductsPerCategory;
  ```

#### Best-Selling Preconfigured Product
- **Purpose**: Displays the single best-selling preconfigured product across all categories.
- **Columns**:
  - `preconfigured_product_id`: The ID of the preconfigured product.
  - `name`: The name of the preconfigured product.
  - `times_ordered`: The number of times the product has been ordered.
- **Refresh Command**:
  ```
  REFRESH MATERIALIZED VIEW BestSellingPreconfiguredProduct;
  ```

#### Automatic Refresh
- The materialized views are automatically refreshed using `pg_cron` at regular intervals:
  - `TopPreconfiguredProductsPerCategory`: Every 6 hours.
  - `BestSellingPreconfiguredProduct`: Every 6 hours (5 minutes after the first view).

### Relationships and Entity Meanings

- **Customer**: Stores information about customers who purchase custom bikes.
- **Orders**: Tracks all orders placed by customers.
- **Category**: Different categories of products (e.g., Bikes , Skies, Surfboards).
- **Part**: Represents customizable components of a product (e.g., Frame, Handlebars).
- **Part Option**: Specific choices for each part (e.g., Carbon Frame, Aluminum Frame).
- **Preconfigured Product**: Base Product models that can be customized.
- **Preconfigured Product Parts**: Default part options for each preconfigured product.
- **Price Adjustment Rule**: Rules that adjust prices when specific part combinations are selected.
- **Stock**: Inventory tracking for each part option.
- **Order Product**: Products included in a customer's order.
- **Order Item**: Specific part options selected for each ordered product.
- **Incompatibility Rule**: Rules defining which part options cannot be used together.

## Main User Actions

1. **Browse Products**
   - Users can see best selling product from the preconfigured products
   - Users can also see top preconfigured products per category
   - Users can also see all prodcuts from a particular category

2. **Customize a Bike**
   - Customise a preconfigured product where you can only change just a few parts that you need to change about that product
   - Customise a product from scratch selecting all parts of that product
   - Choose options for each customizable Part of the product
   - See real-time updates of:
     - Visual representation of the part options
     - Price changes based on selections
     - Component compatibility
     - Inventory availability

3. **Account Management**
   - Registration and login
   - View order history
   - Manage shipping addresses

4. **Checkout Process**
   - Review customized product details
   - Enter shipping information
   - Make payment
   - Receive order confirmation

## Product Page

### Implemented UI Components

Our e-commerce platform provides a rich, interactive shopping experience across several key pages:

#### Home Page
- **Hero Section**: Showcases the best-selling product with image, description, features, and direct "Customize" button
- **Category Sections**: Dynamic sections for each product category (Bicycles, SufBoards, Skies) with:
  - Category heading and description
  - Horizontal product carousel
  - "View all" navigation to category pages
- **Custom Build CTA**: Call-to-action section encouraging users to build a custom bike

#### Category Page
- **Category Header**: Displays category name and description
- **Product Grid**: Responsive grid showing all products in the selected category
- **Product Cards**: Each showing:
  - Product image
  - Product name and price
  - "View Details" and "Customize" buttons
- **Product Details Modal**: Popup showing comprehensive product information

#### Customize Page
- **Category Selection**: Grid of category cards when no specific category is selected
- **BikeCustomizer Component**: The main customization interface with:
  - Step-by-step part selection process
  - Part option cards with images, names, and prices
  - Price calculator showing real-time total
  - Component compatibility validator
  - "Add to Cart" functionality

#### Cart Page
- **Cart Item Listing**: Detailed list of items with:
  - Product image, name, and price
  - Selected component configurations
  - Quantity adjustment controls (plus/minus)
  - Individual item removal
- **Order Summary**: Side panel showing:
  - Subtotal calculation
  - Shipping and tax information
  - Total price
  - "Proceed to Checkout" button
- **Empty Cart State**: Friendly message and CTA when cart is empty

### Implementation

1. **Component Options Availability**

This implementation is focused on determining which options are available for each part of a product based on stock availability.

#### Key Points:
- **Purpose**: Filters out options that are out of stock for each part of the product.
- **Logic**:
  1. Fetch all parts of the product (`fetchPartsForProduct`).
  2. For each part, filter its options using the `isInStock` function from the `useProductStock` hook.
  3. Return a mapping of part IDs to their available options.
- **Hook Used**: `useProductStock` provides utility functions like `isInStock` and `getStockQuantity` to check stock availability.

#### Example Use Case:
If a product has a "Frame" part with options like "Carbon Frame" and "Aluminum Frame", this function ensures only the options that are in stock are shown to the user.

```typescript
// filepath: /Users/zenysisaccount/work/marcus_ecommerce/web/client/hooks/use-product-stock.ts
import { useProductStock } from "@client/hooks/use-product-stock";

const { getStockQuantity, isInStock } = useProductStock(categoryId);

function getAvailableOptions(productId, selectedComponents) {
  const parts = fetchPartsForProduct(productId);

  const availableOptions = {};
  for (const part of parts) {
    const options = part.options.filter((option) => isInStock(option.id));
    availableOptions[part.id] = options;
  }

  return availableOptions;
}
```

2. **Price Calculation**

This implementation is focused on calculating the total price of a product configuration, including any price adjustments.

#### Key Points:
- **Purpose**: Computes the total price of the selected options for a product, considering base prices and price adjustment rules.
- **Logic**:
  1. Iterate over the selected options (`selectedOptions`).
  2. For each selected option, find its base price and any applicable price adjustments using the `getOptionPrice` function from the `useProductRules` hook.
  3. Sum up the prices to calculate the total price.
- **Hook Used**: `useProductRules` provides utility functions like `getOptionPrice` to calculate the price of an option, including adjustments.

#### Example Use Case:
If a user selects a "Carbon Frame" with a base price of $500 and a "High-End Wheels" option with a $200 price adjustment, this function calculates the total price as `$500 + $200 = $700`.

```typescript
// filepath: /Users/zenysisaccount/work/marcus_ecommerce/web/client/hooks/use-product-rules.ts
import { useProductRules } from "@client/hooks/use-product-rules";

const { totalPrice, getOptionPrice } = useProductRules(configuration, parts);

function calculatePrice(productId, selectedOptions) {
  let totalPrice = 0;

  Object.entries(selectedOptions).forEach(([partName, optionId]) => {
    const option = parts.find((part) => part.name === partName)?.options.find((opt) => opt.id === optionId);
    if (option) {
      totalPrice += getOptionPrice(option);
    }
  });

  return totalPrice;
}
```

## Add to Cart Action

When a customer clicks "Add to Cart":

1. The current configuration is validated for completeness and compatibility.
2. Inventory is checked for all selected components.
3. A new order and related records are created.

### Implementation
```typescript
// filepath: /Users/zenysisaccount/work/marcus_ecommerce/web/client/context/cart-context.tsx
import { useCart } from "@client/context/cart-context";

const { addItem } = useCart();

function addToCart(productId, selectedOptions, customName) {
  const product = fetchPreconfiguredProduct(productId);

  const cartItem = {
    id: productId,
    name: product.name,
    price: calculatePrice(productId, selectedOptions),
    image: product.image_url,
    quantity: 1,
    configuration: selectedOptions,
    configDetails: getConfigDetails(selectedOptions, parts),
  };

  addItem(cartItem);
}
```

## Administrative Workflows

Marcus has several key administrative workflows:

### 1. **Product Management**
   - **Create**: Add a new product to the `preconfiguredproduct` table.
     - **Model**: `PreconfiguredProduct`
     - **Fields**: `category_id`, `name`, `base_price`, `image_url`, `description`
   - **Update**: Modify an existing product in the `preconfiguredproduct` table.
     - **Model**: `PreconfiguredProduct`
     - **Fields**: `name`, `base_price`, `image_url`, `description`
   - **Delete**: Remove a product and its associated parts from the `preconfiguredproduct` and `preconfiguredproductparts` tables.

### 2. **Inventory Management**
   - **Create**: Add new inventory for a part option in the `stock` table.
     - **Model**: `Stock`
     - **Fields**: `part_option_id`, `quantity`
   - **Update**: Adjust inventory levels for a part option in the `stock` table.
     - **Model**: `Stock`
     - **Fields**: `quantity`
   - **Delete**: Remove inventory records for discontinued part options.

### 3. **Pricing Management**
   - **Create**: Add a new price adjustment rule in the `priceadjustmentrule` table.
     - **Model**: `PriceAdjustmentRule`
     - **Fields**: `affected_option_id`, `condition_option_id`, `adjusted_price`
   - **Update**: Modify an existing price adjustment rule.
     - **Model**: `PriceAdjustmentRule`
     - **Fields**: `adjusted_price`
   - **Delete**: Remove a price adjustment rule.

### 4. **Order Processing**
   - **Update**: Update the status of an existing order in the `orders` table.
     - **Model**: `Order`
     - **Fields**: `status`
   - **Delete**: Cancel an order and remove associated records from `orderproduct` and `orderitem` tables.

### 5. **Part Management**
   - **Create**: Add a new part or part option in the `part` and `partoption` tables.
     - **Model**: `Part`, `PartOption`
     - **Fields**: 
       - `Part`: `name`, `category_id`, `step`
       - `PartOption`: `part_id`, `name`, `default_price`, `image_url`, `description`
   - **Update**: Modify an existing part or part option.
     - **Model**: `Part`, `PartOption`
     - **Fields**: 
       - `Part`: `name`, `step`
       - `PartOption`: `name`, `default_price`, `image_url`, `description`
   - **Delete**: Remove a part or part option and associated records.

### 6. **Incompatibility Rules**
   - **Create**: Add a new incompatibility rule in the `incompatibilityrule` table.
     - **Model**: `IncompatibilityRule`
     - **Fields**: `part_option_id`, `incompatible_with_option_id`, `message`
   - **Update**: Modify an existing incompatibility rule.
     - **Model**: `IncompatibilityRule`
     - **Fields**: `message`
   - **Delete**: Remove an incompatibility rule.

## New Product Creation

To create a new product, Marcus needs to provide:

1. Basic product information:
   - Name
   - Description
   - Base price
   - Product images
   - Category

2. Component configuration:
   - Select which parts apply to this product
   - Set default options for each part
   - Define incompatibility rules between components

### Preconfigured Products Configurator

Marcus can use a configurator in the admin portal, similar to the one available in the client app, to create or edit preconfigured products. This tool provides an intuitive interface for selecting and customizing default configurations for products.

#### Features of the Configurator:
- **Step-by-Step Part Selection**: Marcus can select parts (e.g., Frame, Wheels, Handlebars) and assign default options for each part.
- **Real-Time Price Calculation**: The configurator calculates the base price dynamically based on the selected default options.
- **Compatibility Validation**: The configurator validates the compatibility of selected parts using the `incompatibilityrule` table.
- **Stock Availability Check**: Ensures that the selected default options are in stock.
- **Preview**: Provides a visual preview of the preconfigured product, including images and descriptions.

#### Workflow:
1. Navigate to the "Preconfigured Products" section in the admin portal.
2. Click "Add New Product" or select an existing product to edit.
3. Use the configurator to:
   - Select parts and default options.
   - Define pricing and descriptions.
   - Validate compatibility and stock availability.
4. Save the configuration, which updates the `preconfiguredproduct` and `preconfiguredproductparts` tables.

---

## Adding New Part Choices

To add a new part choice (e.g., a new rim color):

### UI Process
1. Marcus navigates to the Admin Portal.
2. Selects "Part Management" → "Wheels" category.
3. Clicks "Add Part Option."
4. Fills out a form with:
   - Option name (e.g., "Blue Rim")
   - Description
   - Image upload
   - Default price
   - Initial inventory quantity
5. Saves the new part option.

---

## Setting Prices

Marcus can set prices in three ways:

### 1. Individual Part Option Prices
Each part option has a default price that's applied when selected.

### 2. Price Adjustment Rules
For special pricing on specific combinations of part options.

#### UI Process
1. Marcus navigates to "Price Rules" in the Admin Portal.
2. Clicks "Add Price Rule."
3. Selects a part option to be affected (`affected_option_id`).
4. Selects another part option as the condition (`condition_option_id`).
5. Sets the adjusted price for the affected option when the condition is met.
6. Saves the rule.

## Installation and Setup

### Backend Setup
For detailed instructions on setting up the backend, refer to the [Server README](./server/README.md).

### Frontend Setup
For detailed instructions on setting up the frontend applications (client and admin), refer to the [Web README](./web/README.md).

### Current State of the Applications
1. **Admin UI**:
   - The admin dashboard is not fully connected to the backend yet.
   - You can run the admin UI and browse through its features, but data is currently mocked and not fetched from the backend.

2. **Client Application**:
   - The client-facing store is connected to the backend for most features, such as browsing products and viewing details.
   - The checkout process is not yet connected to create an order in the backend. The current goal is to move the cart from local storage to backend orders.

### Cart Implementation
- The cart is currently implemented using **local storage** in the client application.
- Items added to the cart are stored locally, allowing users to retain their cart even after refreshing the page.
- Future plans include:
  - Integrating the checkout process to create an order in the backend.

## Future Plans

- **Message Brokers**: Plan to integrate message brokers like RabbitMQ to handle tasks such as sending order confirmation emails and other asynchronous workflows.
