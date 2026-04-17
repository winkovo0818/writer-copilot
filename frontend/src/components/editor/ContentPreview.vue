<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  markdown: { type: String, default: '' },
})

marked.setOptions({ breaks: true })

const html = computed(() => {
  if (!props.markdown) return '<p class="empty">正文将在此预览</p>'
  return marked.parse(props.markdown)
})
</script>

<template>
  <div class="content-preview app-card">
    <div class="content-preview__header">
      <h3 class="content-preview__heading">正文预览</h3>
      <div v-if="markdown" class="content-preview__meta">
        {{ markdown.length }} 字
      </div>
    </div>
    <div class="content-preview__body markdown-body" v-html="html" />
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.content-preview {
  padding: 48px;
  min-height: 500px;
  background: $color-white;
}

.content-preview__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 40px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 20px;
}

.content-preview__heading {
  font-family: $font-display;
  font-weight: 300;
  font-size: 2.5rem;
  margin: 0;
  color: $color-black;
  letter-spacing: -0.02em;
}

.content-preview__meta {
  font-size: 14px;
  font-weight: 500;
  color: $color-text-muted;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.content-preview__body {
  font-size: 1.15rem;
  line-height: 1.8;
  letter-spacing: 0.01em;
  color: $color-text-secondary;
  
  // 动画：让内容看起来像是在“生长”
  :deep(p), :deep(h1), :deep(h2), :deep(h3), :deep(pre), :deep(blockquote) {
    animation: contentReveal 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  }

  :deep(h1),
  :deep(h2),
  :deep(h3) {
    font-family: $font-display;
    font-weight: 300;
    color: $color-black;
    margin-top: 1.8em;
    margin-bottom: 0.6em;
  }

  :deep(h1) { font-size: 2.25rem; }
  :deep(h2) { font-size: 2rem; }
  :deep(h3) { font-size: 1.75rem; }

  :deep(p) {
    margin-bottom: 1.5em;
  }

  :deep(pre) {
    font-family: $font-mono;
    font-size: 0.85rem;
    line-height: 1.85;
    padding: 32px;
    border-radius: $radius-section;
    background: #fcfcfc;
    border: 1px solid rgba(0, 0, 0, 0.04);
    box-shadow: $shadow-inset-border;
    overflow: auto;
    margin: 32px 0;
  }

  :deep(code) {
    font-family: $font-mono;
    font-size: 0.85rem;
    background: rgba(0, 0, 0, 0.04);
    padding: 3px 8px;
    border-radius: 6px;
    color: $color-black;
  }

  :deep(blockquote) {
    margin: 32px 0;
    padding: 12px 32px;
    border-left: 2px solid $color-black;
    background: $color-bg-muted;
    border-radius: 0 $radius-lg $radius-lg 0;
    color: $color-text-secondary;
    font-style: italic;
  }

  :deep(.empty) {
    color: $color-text-muted;
    font-style: italic;
    text-align: center;
    margin-top: 150px;
    font-weight: 300;
    font-size: 1.25rem;
  }
}

@keyframes contentReveal {
  from {
    opacity: 0;
    transform: translateY(12px);
    filter: blur(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}
</style>
