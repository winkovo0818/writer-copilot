<script setup>
import { onMounted, ref } from 'vue'
import { knowledgeApi } from '@/api/knowledge'
import { useKnowledgeStore } from '@/stores/knowledge'

const kb = useKnowledgeStore()
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await knowledgeApi.listArticles({ page: 1, page_size: 50 })
    kb.setArticles(data?.articles || [])
  } finally {
    loading.value = false
  }
}

onMounted(load)

defineExpose({
  load,
})
</script>

<template>
  <div class="article-list app-card">
    <div class="article-list__head">
      <h3 class="article-list__title">文章列表</h3>
      <a-button size="small" @click="load">刷新</a-button>
    </div>
    <a-table
      :loading="loading"
      :data-source="kb.articles"
      :pagination="false"
      :columns="[
        { title: '标题', dataIndex: 'title', key: 'title' },
        { title: '标签', dataIndex: 'tags', key: 'tags' },
        { title: '更新时间', dataIndex: 'updated_at', key: 'updated_at' },
      ]"
      row-key="article_id"
      size="middle"
    >
      <template #emptyText>
        <span class="app-muted">暂无文章，可先导入一篇试试。</span>
      </template>
    </a-table>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.article-list {
  padding: 24px;
}

.article-list__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.article-list__title {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.75rem;
  margin: 0;
  color: $color-black;
}
</style>
