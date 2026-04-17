<script setup>
const topic = defineModel('topic', { type: String, default: '' })

defineProps({
  disabled: { type: Boolean, default: false },
})
</script>

<template>
  <div class="topic-input">
    <div class="topic-input__header">
      <label class="topic-input__label">选题意图</label>
      <span class="topic-input__hint">分享你的灵感，AI 将为你延展</span>
    </div>
    <div class="topic-input__canvas">
      <a-textarea
        v-model:value="topic"
        :disabled="disabled"
        class="topic-input__textarea"
        :auto-size="{ minRows: 2, maxRows: 6 }"
        placeholder="在这里输入你想创作的主题..."
        :maxlength="200"
      />
      <!-- 动态底线动画 -->
      <div class="topic-input__underline">
        <div class="topic-input__underline-active" />
      </div>
    </div>
    <div class="topic-input__footer">
      <span class="topic-input__char-count" :class="{ 'is-limit': topic.length >= 200 }">
        {{ topic.length }} / 200
      </span>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.topic-input {
  padding: 8px 0;
}

.topic-input__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 24px;
}

.topic-input__label {
  font-family: $font-display;
  font-weight: 300;
  font-size: 2.25rem;
  color: $color-black;
  letter-spacing: -0.01em;
}

.topic-input__hint {
  font-size: 13px;
  color: $color-text-muted;
  letter-spacing: 0.05em;
  font-style: italic;
}

.topic-input__canvas {
  position: relative;
  margin-bottom: 12px;
}

.topic-input__textarea {
  font-size: 1.5rem !important; // 大号字体，更有冲击力
  line-height: 1.5 !important;
  color: $color-black !important;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: none !important;
  resize: none !important;
  font-family: $font-body;
  font-weight: 300;
  letter-spacing: -0.01em;

  &::placeholder {
    color: rgba(0, 0, 0, 0.1) !important;
    font-weight: 300;
  }

  &:focus {
    & + .topic-input__underline .topic-input__underline-active {
      transform: scaleX(1);
    }
  }
}

.topic-input__underline {
  height: 1px;
  width: 100%;
  background: rgba(0, 0, 0, 0.05);
  margin-top: 16px;
  position: relative;
}

.topic-input__underline-active {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: $color-black;
  transform: scaleX(0);
  transition: transform 0.6s cubic-bezier(0.19, 1, 0.22, 1);
  transform-origin: left;
}

.topic-input__footer {
  display: flex;
  justify-content: flex-end;
}

.topic-input__char-count {
  font-size: 12px;
  font-family: $font-mono;
  color: rgba(0, 0, 0, 0.2);
  transition: color 0.3s ease;
  
  &.is-limit {
    color: #ff4d4f;
  }
}

// 适配禁用状态
:deep(.ant-input-disabled) {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
