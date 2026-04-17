<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  edges: { type: Array, default: () => [] },
})

const root = ref(null)
let simulation = null

function buildGraph() {
  if (!root.value) return
  if (!props.nodes?.length) {
    d3.select(root.value).selectAll('*').remove()
    d3.select(root.value)
      .append('div')
      .attr('class', 'graph-canvas__empty')
      .text('暂无节点，请调整话题或检查图谱数据')
    return
  }
  const w = root.value.clientWidth || 600
  const h = 420
  d3.select(root.value).selectAll('*').remove()

  const svg = d3
    .select(root.value)
    .append('svg')
    .attr('width', w)
    .attr('height', h)
    .attr('viewBox', `0 0 ${w} ${h}`)

  const g = svg.append('g')

  const zoom = d3.zoom().on('zoom', (ev) => {
    g.attr('transform', ev.transform)
  })
  svg.call(zoom)

  const nodeData = props.nodes.map((n, i) => ({
    id: n.name || n.id || String(i),
    name: n.name || n.id || `N${i}`,
    ...n,
  }))

  const names = new Set(nodeData.map((d) => d.id))
  const edgeData = props.edges
    .map((e, i) => ({
      source: e.source ?? e.from,
      target: e.target ?? e.to,
      ...e,
      id: i,
    }))
    .filter((e) => names.has(e.source) && names.has(e.target))

  simulation = d3
    .forceSimulation(nodeData)
    .force(
      'link',
      d3
        .forceLink(edgeData)
        .id((d) => d.id)
        .distance(90),
    )
    .force('charge', d3.forceManyBody().strength(-220))
    .force('center', d3.forceCenter(w / 2, h / 2))
    .force('collision', d3.forceCollide().radius(36))

  const link = g
    .append('g')
    .attr('stroke', 'rgba(0,0,0,0.12)')
    .selectAll('line')
    .data(edgeData)
    .join('line')
    .attr('stroke-width', 1.2)

  const node = g
    .append('g')
    .selectAll('g')
    .data(nodeData)
    .join('g')
    .call(
      d3
        .drag()
        .on('start', (ev, d) => {
          if (!ev.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on('drag', (ev, d) => {
          d.fx = ev.x
          d.fy = ev.y
        })
        .on('end', (ev, d) => {
          if (!ev.active) simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        }),
    )

  node
    .append('circle')
    .attr('r', 28)
    .attr('fill', 'rgba(245, 242, 239, 0.95)')
    .attr('stroke', 'rgba(0,0,0,0.08)')
    .attr('stroke-width', 1)

  node
    .append('text')
    .text((d) => (d.name || '').slice(0, 8))
    .attr('text-anchor', 'middle')
    .attr('dy', 4)
    .attr('font-size', 11)
    .attr('fill', '#4e4e4e')

  simulation.on('tick', () => {
    link
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y)
    node.attr('transform', (d) => `translate(${d.x},${d.y})`)
  })
}

onMounted(() => {
  buildGraph()
})

watch(
  () => [props.nodes, props.edges],
  () => buildGraph(),
  { deep: true },
)

onUnmounted(() => {
  simulation?.stop()
})
</script>

<template>
  <div ref="root" class="graph-canvas" />
</template>

<style scoped lang="scss">
.graph-canvas {
  width: 100%;
  min-height: 420px;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid #e5e5e5;
  box-shadow:
    rgba(0, 0, 0, 0.06) 0 0 0 1px,
    rgba(0, 0, 0, 0.04) 0 1px 2px;
  overflow: hidden;
}

.graph-canvas :deep(.graph-canvas__empty) {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 360px;
  padding: 24px;
  color: #777169;
  font-size: 15px;
  letter-spacing: 0.15px;
}
</style>
