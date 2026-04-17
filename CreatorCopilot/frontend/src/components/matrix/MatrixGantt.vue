<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  articles: { type: Array, default: () => [] },
})

const el = ref(null)
let chart

function render() {
  if (!el.value) return
  if (!chart) chart = echarts.init(el.value)

  const rows = props.articles.length
    ? props.articles
    : [
        { order: 1, title: '示例文章 A', difficulty: 2 },
        { order: 2, title: '示例文章 B', difficulty: 3 },
        { order: 3, title: '示例文章 C', difficulty: 4 },
      ]

  chart.setOption({
    grid: { left: 12, right: 12, top: 32, bottom: 32 },
    xAxis: {
      type: 'category',
      data: rows.map((a) => `#${a.order}`),
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.12)' } },
    },
    yAxis: {
      type: 'value',
      name: '难度',
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.06)' } },
    },
    series: [
      {
        type: 'bar',
        data: rows.map((a) => a.difficulty ?? a.order ?? 1),
        itemStyle: {
          color: '#000000',
          borderRadius: [8, 8, 0, 0],
        },
        barWidth: '48%',
      },
    ],
    tooltip: { trigger: 'axis' },
  })
}

function resize() {
  chart?.resize()
}

onMounted(() => {
  render()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
  chart = null
})

watch(
  () => props.articles,
  () => render(),
  { deep: true },
)
</script>

<template>
  <div ref="el" class="matrix-gantt" />
</template>

<style scoped lang="scss">
.matrix-gantt {
  width: 100%;
  height: 320px;
}
</style>
