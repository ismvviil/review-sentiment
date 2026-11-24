import { fileURLToPath, URL } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API_TARGET = process.env.VITE_PROXY_TARGET ?? 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 5173,
    // In development the browser calls the same origin; Vite forwards to FastAPI (no CORS).
    proxy: {
      '/api': API_TARGET,
      '/health': API_TARGET,
      '/docs': API_TARGET,
      '/openapi.json': API_TARGET,
    },
  },
})
