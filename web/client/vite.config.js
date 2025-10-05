import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` from the root web directory
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '');
  
  // Automatically prepare environment variables for the define object
  const envDefine = {};
  Object.keys(env).forEach(key => {
    envDefine[`import.meta.env.${key}`] = JSON.stringify(env[key]);
  });
  
  return {
    root: path.resolve(__dirname),
    plugins: [react()],
    resolve: {
      alias: {
        '@shared': path.resolve(__dirname, '../shared'),
        '@client': path.resolve(__dirname, './'),
      },
      dedupe: ['react', 'react-dom']
    },
    server: {
      port: 3000,
    },
    build: {
      outDir: path.resolve(__dirname, '../../dist/client'),
    },
    define: envDefine,
    optimizeDeps: {
      include: ['react', 'react-dom', '@stripe/stripe-js', '@stripe/react-stripe-js']
    }
  };
});
