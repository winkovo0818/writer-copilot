<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import * as echarts from 'echarts'
import { feedbackApi } from '@/api/feedback'
import { useStatsStore } from '@/stores/stats'

const stats = useStatsStore()
const loading = ref(false)

const trendEl = ref(null)
let trendChart

async function load() {
  loading.value = true
  try {
    const data = await feedbackApi.dashboard()
    stats.setDashboard(data)
    renderTrend(data?.trends || [])
  } catch (e) {
    message.error(e.message || '加载看板失败')
  } finally {
    loading.value = false
  }
}

function renderTrend(trends) {
  if (!trendEl.value) return
  if (!trendChart) trendChart = echarts.init(trendEl.value)
  trendChart.setOption({
    grid: { left: 48, right: 24, top: 24, bottom: 32 },
    xAxis: {
      type: 'category',
      data: trends.map((t) => t.week),
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.12)' } },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
    },
    series: [
      {
        type: 'line',
        smooth: true,
        data: trends.map((t) => t.views),
        lineStyle: { color: '#000', width: 2 },
        areaStyle: { color: 'rgba(0,0,0,0.04)' },
        symbolSize: 8,
      },
    ],
    tooltip: { trigger: 'axis' },
  })
}

function exportCsv() {
  const d = stats.dashboard
  if (!d) return
  const rows = [
    ['指标', '值'],
    ['本月篇数', d.monthly_summary?.article_count],
    ['平均阅读', d.monthly_summary?.avg_views],
    ['平均互动率', d.monthly_summary?.avg_engagement],
  ]
  const csv = rows.map((r) => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'dashboard-summary.csv'
  a.click()
  URL.revokeObjectURL(url)
}

function resize() {
  trendChart?.resize()
}

onMounted(() => {
  load()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  trendChart?.dispose()
  trendChart = null
})
</script>

<template>
  <div class="page-dash">
    <header class="page-dash__hero">
      <h1 class="app-display-hero">数据看板</h1>
      <p class="page-dash__lead">本月汇总、趋势与爆款排行（对接 /feedback/dashboard）。</p>
    </header>

    <div class="page-dash__actions">
      <a-button type="primary" :loading="loading" @click="load">刷新</a-button>
      <a-button :disabled="!stats.dashboard" @click="exportCsv">导出 CSV</a-button>
    </div>

    <a-spin :spinning="loading">
      <div v-if="stats.dashboard" class="page-dash__grid">
        <div class="app-card page-dash__metric">
          <div class="page-dash__metric-label">本月篇数</div>
          <div class="page-dash__metric-value">
            {{ stats.dashboard.monthly_summary?.article_count }}
          </div>
        </div>
        <div class="app-card page-dash__metric">
          <div class="page-dash__metric-label">平均阅读</div>
          <div class="page-dash__metric-value">
            {{ stats.dashboard.monthly_summary?.avg_views }}
          </div>
        </div>
        <div class="app-card page-dash__metric">
          <div class="page-dash__metric-label">平均互动率</div>
          <div class="page-dash__metric-value">
            {{ stats.dashboard.monthly_summary?.avg_engagement }}
          </div>
        </div>
        <div class="app-card page-dash__metric">
          <div class="page-dash__metric-label">总点赞</div>
          <div class="page-dash__metric-value">
            {{ stats.dashboard.monthly_summary?.total_likes }}
          </div>
        </div>
      </div>

      <div v-if="stats.dashboard" class="page-dash__charts">
        <div class="app-card page-dash__chart">
          <h3 class="page-dash__h3">阅读趋势</h3>
          <div ref="trendEl" class="page-dash__trend" />
        </div>
        <div class="app-card page-dash__chart">
          <h3 class="page-dash__h3">爆款 TOP</h3>
          <a-list :data-source="stats.dashboard.top_articles || []">
            <template #renderItem="{ item, index }">
              <a-list-item>
                <span class="page-dash__rank">{{ index + 1 }}</span>
                {{ item.title }} — {{ item.views }} 阅读 · 互动 {{ item.engagement }}
              </a-list-item>
            </template>
          </a-list>
        </div>
        <div class="app-card page-dash__chart page-dash__wide">
          <h3 class="page-dash__h3">AI 洞察</h3>
          <ul>
            <li v-for="(line, i) in stats.dashboard.ai_insights || []" :key="i">
              {{ line }}
            </li>
          </ul>
        </div>
      </div>
    </a-spin>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-dash__hero {
  margin-bottom: 20px;
}

.page-dash__lead {
  color: $color-text-secondary;
  max-width: 720px;
}

.page-dash__actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.page-dash__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 1024px) {
  .page-dash__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.page-dash__metric {
  padding: 20px;
}

.page-dash__metric-label {
  font-size: 14px;
  color: $color-text-muted;
  letter-spacing: 0.14px;
}

.page-dash__metric-value {
  font-family: $font-display;
  font-weight: 300;
  font-size: 2.25rem;
  color: $color-black;
  margin-top: 8px;
}

.page-dash__charts {
  margin-top: 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.page-dash__wide {
  grid-column: 1 / -1;
}

.page-dash__chart {
  padding: 20px;
}

.page-dash__h3 {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.5rem;
  margin: 0 0 12px;
}

.page-dash__trend {
  width: 100%;
  height: 300px;
}

.page-dash__rank {
  display: inline-block;
  width: 24px;
  font-weight: 600;
  color: $color-black;
}
</style>
