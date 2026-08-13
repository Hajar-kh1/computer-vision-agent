import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// TODO (Student 4):
// - In dev, proxy /api to the backend so the frontend can call
//   fetch('/api/v1/...') without CORS pain:
//     server: { proxy: { '/api': 'http://localhost:8000' } }
// - In production (nginx), the same /api proxy is configured in nginx.conf.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
