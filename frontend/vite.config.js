import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  build: { manifest: true },  // <-- new
  base: "/static/",           // <-- new
  plugins: [svelte()]
})
