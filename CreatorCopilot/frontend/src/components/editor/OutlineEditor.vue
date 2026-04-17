<script setup>
import { ref, watch, onMounted } from 'vue'
import { message } from 'ant-design-vue'

const props = defineProps({
  outline: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm'])

const text = ref('{}')

watch(
  () => props.outline,
  (o) => {
    try {
      if (o) {
        text.value = JSON.stringify(o, null, 2)
      }
    } catch {
      text.value = '{}'
    }
  },
  { immediate: true, deep: true },
)

function onConfirm() {
  try {
    const parsed = JSON.parse(text.value)
    emit('confirm', parsed)
  } catch {
    message.error('大纲 JSON 格式无效')
  }
}
</script>

<template>
  <div class="outline-editor app-card">
    <div class="outline-editor__header">
      <h3 class="outline-editor__heading">大纲确认</h3>
      <p class="outline-editor__desc">可编辑 JSON 配置，确认后将继续写作与配图阶段。</p>
    </div>

    <div class="outline-editor__body">
      <a-textarea
        v-model:value="text"
        class="outline-editor__area"
        :rows="12"
        spellcheck="false"
        placeholder="{ ... }"
      />
    </div>

    <div class="outline-editor__footer">
      <button
        class="app-btn-warm outline-editor__cta"
        :disabled="loading"
        @click="onConfirm"
      >
        <template v-if="loading"><a-spin size="small" /> 正在确认...</template>
        <template v-else>确认大纲并继续</template>
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.outline-editor {
  padding: 40px;
  border-top: 4px solid $color-warm-stone;
}

.outline-editor__header {
  margin-bottom: 32px;
}

.outline-editor__heading {
  font-family: $font-display;
  font-weight: 300;
  font-size: 2.25rem;
  margin: 0 0 12px;
  color: $color-black;
  letter-spacing: -0.01em;
}

.outline-editor__desc {
  margin: 0;
  color: $color-text-secondary;
  font-size: 1.125rem;
  line-height: 1.6;
}

.outline-editor__body {
  margin-bottom: 32px;
}

.outline-editor__area {
  font-family: $font-mono !important;
  font-size: 0.875rem !important;
  line-height: 1.6 !important;
  padding: 24px !important;
  border-radius: $radius-lg !important;
  background: $color-bg-muted !important;
  border: 1px solid $color-border-subtle !important;
  color: $color-text-secondary !important;
  transition: all 0.2s ease !important;

  &:focus {
    background: $color-white !important;
    border-color: $color-black !important;
    box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.04) !important;
  }

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: $color-border;
    border-radius: 3px;
  }
}

.outline-editor__footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 32px;
  border-top: 1px solid $color-border-subtle;
}

.outline-editor__cta {
  width: 100%;
  height: 52px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
