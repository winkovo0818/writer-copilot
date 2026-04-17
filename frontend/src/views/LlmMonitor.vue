<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import * as echarts from 'echarts'
import { llmApi } from '@/api/llm'

const loading = ref(false)
const data = ref(null)

const tableColumns = [
  { title: '任务 ID', dataIndex: 'task_id', key: 'task_id', ellipsis: true },
  { title: '选题', dataIndex: 'topic', key: 'topic' },
  { title: '调用次数', dataIndex: 'calls', key: 'calls', width: 100 },
  { title: '成本 (¥)', dataIndex: 'cost_cny', key: 'cost_cny', width: 120 },
]

const costEl = ref(null)
const pieEl = ref(null)
let costChart
let pieChart

function initCharts() {
  if (costEl.value && !costChart) costChart = echarts.init(costEl.value)
  if (pieEl.value && !pieChart) pieChart = echarts.init(pieEl.value)
}

function render() {
  if (!data.value) return
  initCharts()

  const trend = data.value.cost_trend || []
  costChart?.setOption({
    grid: { left: 48, right: 24, top: 28, bottom: 32 },
    xAxis: {
      type: 'category',
      data: trend.map((d) => d.date?.slice(5) ?? d.date),
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.12)' } },
    },
    yAxis: {
      type: 'value',
      name: '元',
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
    },
    series: [
      {
        type: 'line',
        smooth: true,
        data: trend.map((d) => d.cost_cny),
        lineStyle: { color: '#000000', width: 2 },
        areaStyle: { color: 'rgba(0,0,0,0.06)' },
        symbolSize: 6,
      },
    ],
    tooltip: { trigger: 'axis' },
  })

  const shares = data.value.model_share || []
  const pieData = shares.map((s) => ({ name: s.model, value: s.calls }))
  pieChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, textStyle: { fontSize: 12 } },
    series: [
      {
        type: 'pie',
        radius: ['42%', '68%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: { formatter: '{b}\n{d}%' },
        data: pieData,
        color: ['#000000', '#4e4e4e', '#777169', '#c4c4c4'],
      },
    ],
  })
}

async function load() {
  loading.value = true
  try {
    data.value = await llmApi.monitoring()
    render()
  } catch (e) {
    message.error(e.message || '加载 LLM 监控失败')
  } finally {
    loading.value = false
  }
}

function resize() {
  costChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  load()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  costChart?.dispose()
  pieChart?.dispose()
  costChart = null
  pieChart = null
})

</script>

<template>
  <div class="page-llm">
    <header class="page-llm__hero">
      <h1 class="app-display-hero">LLM 监控</h1>
      <p class="page-llm__lead">
        成本趋势、模型调用占比、降级与失败率、高消费任务（数据来自后端
        <code class="page-llm__code">/api/v1/llm/monitoring</code>，可替换为真实计量）。
      </p>
    </header>

    <div class="page-llm__actions">
      <a-button type="primary" :loading="loading" @click="load">刷新</a-button>
    </div>

    <a-spin :spinning="loading">
      <template v-if="data">
        <div class="page-llm__kpis">
          <div class="app-card page-llm__kpi">
            <div class="page-llm__kpi-label">今日累计成本</div>
            <div class="page-llm__kpi-value">
              ¥{{ data.daily_cost_cny?.toFixed?.(2) ?? data.daily_cost_cny }}
            </div>
            <div class="page-llm__kpi-sub app-muted">
              限额 ¥{{ data.daily_cost_limit_cny ?? '—' }}
            </div>
          </div>
          <div class="app-card page-llm__kpi">
            <div class="page-llm__kpi-label">降级次数</div>
            <div class="page-llm__kpi-value">{{ data.routing?.degradation_count ?? '—' }}</div>
            <div class="page-llm__kpi-sub app-muted">路由降档（示意）</div>
          </div>
          <div class="app-card page-llm__kpi">
            <div class="page-llm__kpi-label">失败率</div>
            <div class="page-llm__kpi-value">
              {{ ((data.routing?.failure_rate ?? 0) * 100).toFixed(2) }}%
            </div>
            <div class="page-llm__kpi-sub app-muted">
              失败 {{ data.routing?.failure_count ?? 0 }} / 总调用
              {{ data.routing?.total_calls ?? '—' }}
            </div>
          </div>
        </div>

        <div class="page-llm__charts">
          <div class="app-card page-llm__chart">
            <h3 class="page-llm__h3">成本趋势</h3>
            <div ref="costEl" class="page-llm__plot" />
          </div>
          <div class="app-card page-llm__chart">
            <h3 class="page-llm__h3">各模型调用占比</h3>
            <div ref="pieEl" class="page-llm__plot" />
          </div>
        </div>

        <div class="app-card page-llm__table">
          <h3 class="page-llm__h3">Top 消费任务</h3>
          <a-table
            :data-source="data.top_tasks || []"
            :pagination="false"
            size="middle"
            row-key="task_id"
            :columns="tableColumns"
          >
            <template #bodyCell="{ column, text }">
              <template v-if="column.key === 'cost_cny'">
                {{ text != null ? Number(text).toFixed(2) : '—' }}
              </template>
              <template v-else>{{ text }}</template>
            </template>
          </a-table>
        </div>
      </template>
    </a-spin>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-llm__hero {
  margin-bottom: 20px;
}

.page-llm__lead {
  color: $color-text-secondary;
  max-width: 800px;
  line-height: 1.6;
  letter-spacing: 0.16px;
}

.page-llm__code {
  font-family: $font-mono;
  font-size: 0.88rem;
  background: rgba(245, 242, 239, 0.9);
  padding: 2px 8px;
  border-radius: 6px;
}

.page-llm__actions {
  margin-bottom: 20px;
}

.page-llm__kpis {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

@media (max-width: 900px) {
  .page-llm__kpis {
    grid-template-columns: 1fr;
  }
}

.page-llm__kpi {
  padding: 20px;
}

.page-llm__kpi-label {
  font-size: 14px;
  color: $color-text-muted;
  letter-spacing: 0.14px;
}

.page-llm__kpi-value {
  font-family: $font-display;
  font-weight: 300;
  font-size: 2rem;
  color: $color-black;
  margin-top: 8px;
}

.page-llm__kpi-sub {
  margin-top: 6px;
  font-size: 13px;
}

.page-llm__charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 960px) {
  .page-llm__charts {
    grid-template-columns: 1fr;
  }
}

.page-llm__chart {
  padding: 20px;
}

.page-llm__h3 {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.5rem;
  margin: 0 0 8px;
}

.page-llm__plot {
  width: 100%;
  height: 300px;
}

.page-llm__table {
  padding: 20px;
}
</style>
