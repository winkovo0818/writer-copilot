import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (/[\\/]echarts[\\/]/.test(id)) return 'vendor-echarts'
          if (/[\\/]d3[\\/]/.test(id)) return 'vendor-d3'
          if (/[\\/]ant-design-vue[\\/]/.test(id) || /[\\/]@ant-design[\\/]icons-vue[\\/]/.test(id)) {
            return 'vendor-antd'
          }
          if (/[\\/]node_modules[\\/]vue[\\/]/.test(id)) return 'vendor-vue'
          if (/[\\/]vue-router[\\/]/.test(id)) return 'vendor-vue-router'
          if (/[\\/]pinia[\\/]/.test(id)) return 'vendor-pinia'
          if (/[\\/]axios[\\/]/.test(id)) return 'vendor-axios'
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
