import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  css: {
    postcss: false,
  },
  server: {
    port: 5173,
    open: true,
    strictPort: true,  // fail fast if 5173 is taken instead of silently moving
  }
})
