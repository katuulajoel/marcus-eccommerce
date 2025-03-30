import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname),
  resolve: {
    alias: {
      '@shared': path.resolve(__dirname, '../shared'),
      '@client': path.resolve(__dirname, './'),
    },
  },
  server: {
    port: 3000,
  },
  build: {
    outDir: path.resolve(__dirname, '../../dist/client'),
  },
});
