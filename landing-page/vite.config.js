import { defineConfig } from 'vite'
import { resolve } from 'path'

const pages = [
  'about', 'admin', 'download', 'forgot-password', 'help-center',
  'index', 'login', 'payment', 'privacy', 'refund', 'register',
  'reset-password', 'signup', 'success', 'support', 'terms'
]

const inputs = {}
pages.forEach(p => {
  inputs[p] = resolve(__dirname, `${p === 'index' ? 'index' : p}.html`)
})

export default defineConfig({
  root: '.',
  build: {
    rollupOptions: {
      input: inputs,
    },
  },
  server: {
    port: 5173,
    open: true,
    strictPort: true,
  }
})
