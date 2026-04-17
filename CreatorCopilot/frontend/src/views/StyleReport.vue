<script setup>
import { ref, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import * as echarts from 'echarts'
import { styleApi } from '@/api/style'

const period = ref('2026-04')
const report = ref(null)
const drift = ref([])
const loading = ref(false)

const radarEl = ref(null)
let radarChart

async function load() {
  loading.value = true
  try {
    const [r, d] = await Promise.all([
      styleApi.report(period.value),
      styleApi.driftAlerts(),
    ])
    report.value = r
    drift.value = d?.alerts || []
  } catch (e) {
    message.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function renderRadar() {
  if (!radarEl.value || !report.value) return
  if (!radarChart) radarChart = echarts.init(radarEl.value)
  const vs = report.value.vs_last_period || {}
  const keys = Object.keys(vs)
  radarChart.setOption({
    radar: {
      indicator: keys.map((k) => ({ name: k, max: 100 })),
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: keys.map(() => 72),
            name: '本期',
            areaStyle: { color: 'rgba(0,0,0,0.08)' },
            lineStyle: { color: '#000' },
          },
        ],
      },
    ],
  })
}

onMounted(load)

watch(
  () => report.value,
  () => {
    renderRadar()
  },
)

</script>

<template>
  <div class="page-style">
    <header class="page-style__hero">
      <h1 class="app-display-hero">风格报告</h1>
      <p class="page-style__lead">月度趋势、漂移预警与基线对比（对接后端模拟数据）。</p>
    </header>

    <div class="page-style__bar app-card">
      <span>周期（YYYY-MM）</span>
      <a-input v-model:value="period" style="width: 140px" placeholder="2026-04" />
      <a-button type="primary" :loading="loading" @click="load">刷新</a-button>
    </div>

    <a-spin :spinning="loading">
      <div v-if="report" class="page-style__grid">
        <div class="app-card page-style__card">
          <h3 class="page-style__h3">概览</h3>
          <p>文章数：{{ report.article_count }}</p>
          <p>句长趋势：{{ report.trends?.sentence_length_trend }}</p>
          <p>词汇趋势：{{ report.trends?.vocabulary_trend }}</p>
        </div>
        <div class="app-card page-style__card">
          <h3 class="page-style__h3">漂移预警</h3>
          <a-alert
            v-for="(a, i) in report.drift_alerts || []"
            :key="i"
            :message="a.dimension"
            :description="a.message"
            :type="a.severity === 'warning' ? 'warning' : 'info'"
            show-icon
            class="page-style__alert"
          />
        </div>
        <div class="app-card page-style__card">
          <h3 class="page-style__h3">多维对比（雷达示意）</h3>
          <div ref="radarEl" class="page-style__radar" />
        </div>
        <div class="app-card page-style__card">
          <h3 class="page-style__h3">建议</h3>
          <ul>
            <li v-for="(s, i) in report.suggestions || []" :key="i">{{ s }}</li>
          </ul>
        </div>
      </div>
    </a-spin>

    <div v-if="drift?.length" class="app-card page-style__extra">
      <h3 class="page-style__h3">实时漂移列表</h3>
      <p v-for="(x, i) in drift" :key="i">
        {{ x.dimension }}：{{ x.current }} vs 基线 {{ x.baseline }}（{{ x.change }}）
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-style__hero {
  margin-bottom: 24px;
}

.page-style__lead {
  color: $color-text-secondary;
  max-width: 720px;
}

.page-style__bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.page-style__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

@media (max-width: 900px) {
  .page-style__grid {
    grid-template-columns: 1fr;
  }
}

.page-style__card {
  padding: 20px;
}

.page-style__h3 {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.5rem;
  margin: 0 0 12px;
}

.page-style__alert {
  margin-bottom: 8px;
}

.page-style__radar {
  width: 100%;
  height: 280px;
}

.page-style__extra {
  margin-top: 20px;
  padding: 20px;
}
</style>
