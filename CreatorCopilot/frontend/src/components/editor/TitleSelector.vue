<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  titles: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const selectedId = ref(null)
const editedTitle = ref('')

watch(
  () => props.titles,
  (list) => {
    if (list?.length && selectedId.value == null) {
      selectedId.value = list[0].id
    }
  },
  { immediate: true },
)

const emit = defineEmits(['confirm'])

function onConfirm() {
  emit('confirm', {
    selectedId: selectedId.value,
    editedTitle: editedTitle.value?.trim() || undefined,
  })
}
</script>

<template>
  <div class="title-selector app-card">
    <div class="title-selector__header">
      <h3 class="title-selector__heading">选择标题</h3>
      <p class="title-selector__desc">点选候选标题，或在下框中直接编辑新标题后确认。</p>
    </div>

    <div class="title-selector__list">
      <div
        v-for="t in titles"
        :key="t.id"
        class="title-selector__item"
        :class="{ 'is-selected': selectedId === t.id }"
        @click="selectedId = t.id"
      >
        <div class="title-selector__radio-circle">
          <div v-if="selectedId === t.id" class="title-selector__radio-dot" />
        </div>
        <div class="title-selector__content">
          <div class="title-selector__text">{{ t.text }}</div>
          <div v-if="t.reason" class="title-selector__reason">{{ t.reason }}</div>
        </div>
      </div>
    </div>

    <div class="title-selector__footer">
      <a-input
        v-model:value="editedTitle"
        class="title-selector__edit"
        placeholder="或直接输入自定义标题（可选）"
        allow-clear
      />
      <button
        class="app-btn-warm title-selector__cta"
        :disabled="loading"
        @click="onConfirm"
      >
        <template v-if="loading"><a-spin size="small" /> 正在确认...</template>
        <template v-else>确认标题并继续</template>
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.title-selector {
  padding: 40px;
  border-top: 4px solid $color-warm-stone;
}

.title-selector__header {
  margin-bottom: 32px;
}

.title-selector__heading {
  font-family: $font-display;
  font-weight: 300;
  font-size: 2.25rem;
  margin: 0 0 12px;
  color: $color-black;
  letter-spacing: -0.01em;
}

.title-selector__desc {
  margin: 0;
  color: $color-text-secondary;
  font-size: 1.125rem;
  line-height: 1.6;
}

.title-selector__list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.title-selector__item {
  display: flex;
  gap: 20px;
  padding: 24px;
  border-radius: $radius-lg;
  border: 1px solid $color-border-subtle;
  background: $color-white;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: $shadow-outline;

  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-level-1;
    border-color: $color-border;
  }

  &.is-selected {
    background: $color-bg-muted;
    border-color: $color-black;
    box-shadow: $shadow-level-1;
  }
}

.title-selector__radio-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid $color-border;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4px;
  transition: all 0.2s ease;

  .is-selected & {
    border-color: $color-black;
  }
}

.title-selector__radio-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: $color-black;
  animation: scaleIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes scaleIn {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

.title-selector__content {
  flex: 1;
}

.title-selector__text {
  font-size: 1.25rem;
  font-weight: 500;
  color: $color-black;
  line-height: 1.4;
}

.title-selector__reason {
  font-size: 15px;
  color: $color-text-muted;
  margin-top: 8px;
  line-height: 1.5;
}

.title-selector__footer {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 32px;
  border-top: 1px solid $color-border-subtle;
}

.title-selector__edit {
  border-radius: $radius-md !important;
  background: $color-bg-muted !important;
  border: none !important;
  height: 48px !important;
  font-size: 16px !important;

  &:focus {
    background: $color-white !important;
    box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.04) !important;
  }
}

.title-selector__cta {
  width: 100%;
  height: 52px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
