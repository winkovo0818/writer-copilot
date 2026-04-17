<script setup>
const imageSource = defineModel({ type: String, default: 'random' })
defineProps({
  disabled: { type: Boolean, default: false },
})
</script>

<template>
  <div class="image-selector">
    <a-segmented
      v-model:value="imageSource"
      :disabled="disabled"
      class="image-selector__segmented"
      :options="[
        { label: '随机推荐', value: 'random' },
        { label: 'Pexels 高清', value: 'pexels' },
      ]"
    />
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.image-selector {
  display: inline-block;
}

:deep(.ant-segmented) {
  background: rgba(0, 0, 0, 0.04) !important;
  padding: 4px;
  border-radius: 999px;
  border: none;
  
  .ant-segmented-item {
    border-radius: 999px;
    padding: 4px 16px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    color: $color-text-muted;
    
    &:hover {
      color: $color-black;
    }
  }
  
  .ant-segmented-item-selected {
    background: $color-white !important;
    box-shadow: $shadow-card !important;
    color: $color-black !important;
    font-weight: 600;
  }

  .ant-segmented-thumb {
    border-radius: 999px;
    background: $color-white;
  }
}
</style>
