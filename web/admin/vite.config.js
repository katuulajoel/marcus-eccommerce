import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': path.resolve(__dirname, '../../web/shared'),
      '@admin': path.resolve(__dirname, './'),
    },
  },
  server: {
    port: 3001,
  },
  build: {
    outDir: '../../dist/admin',
  },
});
