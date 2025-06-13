import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://conversational-crypto-web-chat-e36a-4zot3izie.vercel.app',
        changeOrigin: true
      }
    }
  }
}) 
