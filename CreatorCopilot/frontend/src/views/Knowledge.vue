<script setup>
import { ref } from 'vue'
import ArticleList from '@/components/knowledge/ArticleList.vue'
import ArticleImport from '@/components/knowledge/ArticleImport.vue'
import { knowledgeApi } from '@/api/knowledge'
import { message } from 'ant-design-vue'

const listRef = ref(null)
const searchQ = ref('')
const searchLoading = ref(false)
const searchResults = ref([])

async function onSearch() {
  if (searchQ.value.trim().length < 2) {
    message.warning('检索词至少 2 个字符')
    return
  }
  searchLoading.value = true
  try {
    const data = await knowledgeApi.search({ q: searchQ.value.trim(), top_k: 8 })
    searchResults.value = data?.results || []
  } catch (e) {
    message.error(e.message || '检索失败')
  } finally {
    searchLoading.value = false
  }
}

function onImported() {
  listRef.value?.load?.()
}
</script>

<template>
  <div class="page-knowledge">
    <header class="page-knowledge__hero">
      <h1 class="app-display-hero">知识库</h1>
      <p class="page-knowledge__lead">导入文章、语义检索与列表管理。</p>
    </header>

    <div class="page-knowledge__grid">
      <ArticleImport @imported="onImported" />
      <ArticleList ref="listRef" />
    </div>

    <div class="page-knowledge__search app-card">
      <h3 class="page-knowledge__h3">语义检索</h3>
      <a-input-search
        v-model:value="searchQ"
        placeholder="输入问题或关键词"
        size="large"
        :loading="searchLoading"
        enter-button="检索"
        @search="onSearch"
      />
      <a-list
        v-if="searchResults.length"
        class="page-knowledge__results"
        :data-source="searchResults"
        item-layout="vertical"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta :title="item.section_heading || '片段'">
              <template #description>
                <span>{{ item.content }}</span>
                <span class="app-muted">（score: {{ item.score?.toFixed?.(3) ?? item.score }}）</span>
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-knowledge__hero {
  margin-bottom: 28px;
}

.page-knowledge__lead {
  font-size: 1.125rem;
  line-height: 1.6;
  letter-spacing: 0.18px;
  color: $color-text-secondary;
  margin: 12px 0 0;
  max-width: 640px;
}

.page-knowledge__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

@media (max-width: 1024px) {
  .page-knowledge__grid {
    grid-template-columns: 1fr;
  }
}

.page-knowledge__search {
  margin-top: 24px;
  padding: 24px;
}

.page-knowledge__h3 {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.75rem;
  margin: 0 0 16px;
  color: $color-black;
}

.page-knowledge__results {
  margin-top: 20px;
}
</style>
