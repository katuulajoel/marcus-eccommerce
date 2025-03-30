import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname),
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': path.resolve(__dirname, '../shared'),
      '@admin': path.resolve(__dirname, './'),
    },
  },
  server: {
    port: 3001, 
  },
  build: {
    outDir: path.resolve(__dirname, '../../dist/admin'),
  },
});