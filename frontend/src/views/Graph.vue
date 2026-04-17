<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import GraphCanvas from '@/components/graph/GraphCanvas.vue'
import { graphApi } from '@/api/graph'

const topic = ref('LangGraph')
const depth = ref(2)
const loading = ref(false)
const nodes = ref([])
const edges = ref([])
const gaps = ref([])

async function loadContext() {
  loading.value = true
  try {
    const data = await graphApi.getContext({
      topic: topic.value.trim() || 'LangGraph',
      depth: depth.value,
    })
    nodes.value = data?.nodes || []
    edges.value = data?.edges || []
  } catch (e) {
    message.error(e.message || '加载子图失败')
    nodes.value = []
    edges.value = []
  } finally {
    loading.value = false
  }
}

async function loadGaps() {
  try {
    const data = await graphApi.getGaps({ limit: 8 })
    gaps.value = data?.gaps || []
  } catch {
    gaps.value = []
  }
}

onMounted(() => {
  loadContext()
  loadGaps()
})
</script>

<template>
  <div class="page-graph">
    <header class="page-graph__hero">
      <h1 class="app-display-hero">知识图谱</h1>
      <p class="page-graph__lead">话题子图可视化、拖拽与缩放；Gap 列表辅助选题。</p>
    </header>

    <div class="page-graph__toolbar app-card">
      <a-input
        v-model:value="topic"
        placeholder="中心概念名称"
        style="max-width: 280px"
        @press-enter="loadContext"
      />
      <span class="page-graph__label">深度</span>
      <a-slider v-model:value="depth" :min="1" :max="3" :style="{ width: '160px' }" />
      <a-button type="primary" :loading="loading" @click="loadContext">加载子图</a-button>
    </div>

    <a-spin :spinning="loading">
      <GraphCanvas :nodes="nodes" :edges="edges" />
    </a-spin>

    <div v-if="gaps.length" class="page-graph__gaps app-card">
      <h3 class="page-graph__h3">未覆盖概念（Gap）</h3>
      <a-tag v-for="(g, i) in gaps" :key="i" class="page-graph__tag">
        {{ g.name }} · {{ g.category }}
      </a-tag>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-graph__hero {
  margin-bottom: 24px;
}

.page-graph__lead {
  font-size: 1.125rem;
  color: $color-text-secondary;
  margin: 12px 0 0;
  max-width: 680px;
}

.page-graph__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.page-graph__label {
  font-size: 14px;
  color: $color-text-muted;
}

.page-graph__gaps {
  margin-top: 24px;
  padding: 24px;
}

.page-graph__h3 {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.5rem;
  margin: 0 0 12px;
}

.page-graph__tag {
  margin-bottom: 8px;
}
</style>
