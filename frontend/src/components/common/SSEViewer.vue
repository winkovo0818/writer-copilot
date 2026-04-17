<script setup>
import { computed } from 'vue'

const props = defineProps({
  lines: { type: Array, default: () => [] },
  maxLines: { type: Number, default: 200 },
})

const visible = computed(() => props.lines.slice(-props.maxLines))
</script>

<template>
  <div class="sse-viewer app-card">
    <div class="sse-viewer__header">
      <span class="sse-viewer__dot" />
      <span class="sse-viewer__title">SSE 实时流调试</span>
    </div>
    <div class="sse-viewer__container">
      <pre v-if="visible.length" class="sse-viewer__body">{{ visible.join('\n') }}</pre>
      <div v-else class="sse-viewer__empty">暂无实时数据流</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.sse-viewer {
  padding: 0;
  overflow: hidden;
  border-color: $color-border-subtle;
}

.sse-viewer__header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: $color-bg-muted;
  border-bottom: 1px solid $color-border-subtle;
}

.sse-viewer__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.sse-viewer__title {
  font-size: 13px;
  font-weight: 600;
  color: $color-text-muted;
  letter-spacing: 0.14px;
  text-transform: uppercase;
}

.sse-viewer__container {
  padding: 16px 24px;
  background: $color-white;
}

.sse-viewer__body {
  margin: 0;
  height: 200px;
  overflow-y: auto;
  font-family: $font-mono;
  font-size: 13px;
  line-height: 1.6;
  color: $color-text-secondary;
  white-space: pre-wrap;
  word-break: break-all;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: $color-border;
    border-radius: 3px;
  }
}

.sse-viewer__empty {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $color-text-muted;
  font-style: italic;
  font-size: 14px;
}
</style>
