<script setup>
defineProps({
  tip: { type: String, default: '加载中…' },
})
</script>

<template>
  <div class="cc-loading">
    <a-spin size="large" :tip="tip" />
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.cc-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: $color-text-muted;
}
</style>
