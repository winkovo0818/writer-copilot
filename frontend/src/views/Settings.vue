<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'

const user = useUserStore()
const apiBase = ref(import.meta.env.VITE_API_BASE || '/api/v1')

function save() {
  message.info('前端配置以构建时环境变量为准；开发环境代理见 vite.config.js')
}
</script>

<template>
  <div class="page-settings">
    <header class="page-settings__hero">
      <h1 class="app-display-hero">设置</h1>
      <p class="page-settings__lead">账户与偏好（占位）；API 基路径当前为 {{ apiBase }}。</p>
    </header>

    <div class="app-card page-settings__card">
      <h3 class="page-settings__h3">显示名称</h3>
      <a-input v-model:value="user.displayName" style="max-width: 320px" />
    </div>

    <a-button type="primary" class="page-settings__btn" @click="save">保存（示意）</a-button>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-settings__hero {
  margin-bottom: 24px;
}

.page-settings__lead {
  color: $color-text-secondary;
  max-width: 640px;
}

.page-settings__card {
  padding: 24px;
  margin-bottom: 16px;
  max-width: 560px;
}

.page-settings__h3 {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.5rem;
  margin: 0 0 12px;
}

.page-settings__btn {
  margin-top: 8px;
}
</style>
