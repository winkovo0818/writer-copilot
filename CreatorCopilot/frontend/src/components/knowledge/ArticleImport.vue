<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { knowledgeApi } from '@/api/knowledge'

const title = ref('')
const content = ref('')
const tags = ref('')
const loading = ref(false)

const emit = defineEmits(['imported'])

async function onSubmit() {
  if (!title.value.trim() || !content.value.trim()) {
    message.warning('请填写标题与正文')
    return
  }
  loading.value = true
  try {
    await knowledgeApi.importArticle({
      title: title.value.trim(),
      content: content.value,
      tags: tags.value || undefined,
    })
    message.success('导入已提交')
    emit('imported')
    title.value = ''
    content.value = ''
    tags.value = ''
  } catch (e) {
    message.error(e.message || '导入失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="article-import app-card">
    <h3 class="article-import__title">单篇导入</h3>
    <a-form layout="vertical" @submit.prevent="onSubmit">
      <a-form-item label="标题" required>
        <a-input v-model:value="title" placeholder="文章标题" />
      </a-form-item>
      <a-form-item label="正文 Markdown" required>
        <a-textarea v-model:value="content" :rows="10" placeholder="正文内容" />
      </a-form-item>
      <a-form-item label="标签（逗号分隔）">
        <a-input v-model:value="tags" placeholder="例如：Python, LangGraph" />
      </a-form-item>
      <a-button type="primary" html-type="submit" :loading="loading">导入</a-button>
    </a-form>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.article-import {
  padding: 24px;
}

.article-import__title {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.75rem;
  margin: 0 0 16px;
  color: $color-black;
}
</style>
