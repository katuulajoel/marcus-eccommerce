# Marcus eCommerce Frontend

This directory contains the frontend applications for Marcus eCommerce, structured as a monorepo using Vite and React.

## Project Structure

```
web/
├── client/         # Customer-facing eCommerce application
├── admin/          # Admin dashboard application
└── shared/         # Shared components, hooks, and utilities
    ├── components/
    └── hooks/
```

## Setup Instructions

1. First, ensure you have Node.js (v16 or later) installed
2. Navigate to the project root directory
3. Install dependencies:

```bash
npm install
```

## Development

The project contains two separate applications that can be run independently:

### Client Application (Customer-facing Store)

```bash
# From project root
npm run dev:client

# Or from web directory
cd ..
npm run dev:client
```

This will start the development server at http://localhost:3000

### Admin Application (Admin Dashboard)

```bash
# From project root
npm run dev:admin

# Or from web directory
cd ..
npm run dev:admin
```

This will start the development server at http://localhost:3001

## Building for Production

To build both applications for production:

```bash
npm run build
```

This will create optimized builds in the `dist/client` and `dist/admin` directories.

To build individual applications:

```bash
# Build only client application
npm run build:client

# Build only admin application
npm run build:admin
```

## Shared Components

Shared components and hooks are available in the `shared` directory and can be imported in either application using the configured aliases:

```jsx
// In client application
import Button from '@shared/components/Button';
import useApi from '@shared/hooks/useApi';

// In admin application
import Button from '@shared/components/Button';
import useApi from '@shared/hooks/useApi';
```

## Configuration

Each application has its own Vite configuration file:

- Root config: `/vite.config.js` - Defines shared aliases
- Client config: `/web/client/vite.config.js` - Client-specific settings
- Admin config: `/web/admin/vite.config.js` - Admin-specific settings

### Environment Variables

Environment variables are used to configure the application. You can define them in `.env` or `.env.local` files located in the `web` directory. The `.env.local` file is ignored by version control and can be used for local development.

Example `.env.local` file:

```bash
VITE_API_BASE_URL=http://localhost:8000/
```

Ensure that all required variables are defined before running the application. The following variables are commonly used:

- `VITE_API_BASE_URL`: Base URL for the API
- `VITE_<OTHER_VARIABLES>`: Add any additional variables as needed

For production, ensure the environment variables are properly set in your deployment environment.
