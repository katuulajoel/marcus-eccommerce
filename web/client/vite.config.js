import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': path.resolve(__dirname, '../../web/shared'),
      '@client': path.resolve(__dirname, './'),
    },
  },
  server: {
    port: 3000,
  },
  build: {
    outDir: '../../dist/client',
  },
});
