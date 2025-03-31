/**
 * Centralized environment variable access
 * This ensures consistent environment variable access across client and admin apps
 */

// Common environment variables with type safety
export const env = {
  // API settings
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL as string || 'http://localhost:8000/',
  
  // App settings
  NODE_ENV: import.meta.env.MODE as string,
  isDevelopment: import.meta.env.MODE === 'development',
  isProduction: import.meta.env.MODE === 'production',
  
  // Get any environment variable with type safety
  get: <T>(key: string, fallback?: T): T => {
    const value = import.meta.env[key];
    return value !== undefined ? value as unknown as T : fallback as T;
  }
};

// Helper function to log environment details in dev mode
export const logEnvironmentInfo = () => {
  if (env.isDevelopment) {
    console.log('Environment Info:');
    console.log('- API Base URL:', env.API_BASE_URL);
    console.log('- Mode:', env.NODE_ENV);
    
    // Log any other explicitly defined VITE_ environment variables
    Object.keys(import.meta.env).forEach(key => {
      if (key.startsWith('VITE_') && key !== 'VITE_API_BASE_URL') {
        console.log(`- ${key}:`, import.meta.env[key]);
      }
    });
  }
};

// Export common environment variables directly for convenience
export const { API_BASE_URL, isDevelopment, isProduction } = env;
