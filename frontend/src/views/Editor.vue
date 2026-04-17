<script setup>
import { ref, computed, shallowRef } from 'vue'
import { message } from 'ant-design-vue'
import TopicInput from '@/components/editor/TopicInput.vue'
import ImageSelector from '@/components/editor/ImageSelector.vue'
import TitleSelector from '@/components/editor/TitleSelector.vue'
import OutlineEditor from '@/components/editor/OutlineEditor.vue'
import ContentPreview from '@/components/editor/ContentPreview.vue'
import SSEViewer from '@/components/common/SSEViewer.vue'
import { useEditorStore } from '@/stores/editor'
import { streamArticle, streamConfirmTitle, streamConfirmOutline } from '@/api/article'
import { readEventStream } from '@/utils/sse.js'

const editor = useEditorStore()

const topic = ref('')
const imageSource = ref('random')
const sseLines = ref([])
const contentMd = ref('')
const titles = ref([])
const outlineDraft = ref(null)
const showTitle = ref(false)
const showOutline = ref(false)
const streaming = ref(false)
const resumeBusy = ref(false)

const abortRef = shallowRef(null)

const stepIndex = ref(0)
const stageMap = {
  analyze: 0,
  title: 1,
  outline: 2,
  write: 3,
  image: 4,
}

const steps = [
  { title: '分析' },
  { title: '标题' },
  { title: '大纲' },
  { title: '写作' },
  { title: '配图' },
]

const canStart = computed(
  () => topic.value.trim().length >= 5 && !streaming.value && !resumeBusy.value,
)

function log(event, data) {
  const line = `${new Date().toISOString().slice(11, 23)} ${event} ${typeof data === 'string' ? data : JSON.stringify(data)}`
  sseLines.value = [...sseLines.value, line].slice(-300)
}

async function consumeStream(response, afterInterrupt) {
  if (!response.ok) {
    const t = await response.text()
    throw new Error(t || `HTTP ${response.status}`)
  }
  await readEventStream(response.body, (event, data) => {
    log(event, data)
    if (event === 'start' && data?.task_id) {
      editor.taskId = data.task_id
    }
    if (event === 'stage' && data?.node) {
      const i = stageMap[data.node]
      if (i !== undefined) stepIndex.value = i
    }
    if (event === 'titles' && data?.titles) {
      titles.value = data.titles
    }
    if (event === 'outline' && data) {
      outlineDraft.value = data
    }
    if (event === 'content' && data?.chunk) {
      contentMd.value += data.chunk
    }
    if (event === 'need_input') {
      if (data?.stage === 'title') {
        titles.value = data.titles || titles.value
        showTitle.value = true
        showOutline.value = false
      } else if (data?.stage === 'outline') {
        outlineDraft.value = data.outline ?? outlineDraft.value
        showOutline.value = true
        showTitle.value = false
      }
    }
    if (event === 'error') {
      message.error(data?.message || '创作流错误')
    }
    if (event === 'done') {
      message.success('本篇创作流程已完成')
      stepIndex.value = 5
      showTitle.value = false
      showOutline.value = false
    }
  })
  if (afterInterrupt) afterInterrupt()
}

async function onStart() {
  editor.reset()
  contentMd.value = ''
  sseLines.value = []
  titles.value = []
  outlineDraft.value = null
  showTitle.value = false
  showOutline.value = false
  stepIndex.value = 0
  streaming.value = true
  const ac = new AbortController()
  abortRef.value = ac
  try {
    const res = await streamArticle({
      topic: topic.value.trim(),
      imageSource: imageSource.value,
      signal: ac.signal,
    })
    await consumeStream(res, null)
  } catch (e) {
    if (e.name !== 'AbortError') message.error(e.message || '启动失败')
  } finally {
    streaming.value = false
    abortRef.value = null
  }
}

function onCancel() {
  abortRef.value?.abort()
}

async function onTitleConfirm({ selectedId, editedTitle }) {
  if (!editor.taskId) return
  resumeBusy.value = true
  showTitle.value = false
  const ac = new AbortController()
  abortRef.value = ac
  try {
    const res = await streamConfirmTitle({
      taskId: editor.taskId,
      selectedId: editedTitle ? undefined : selectedId,
      editedTitle,
      signal: ac.signal,
    })
    await consumeStream(res, null)
  } catch (e) {
    if (e.name !== 'AbortError') message.error(e.message || '确认标题失败')
    showTitle.value = true
  } finally {
    resumeBusy.value = false
    abortRef.value = null
  }
}

async function onOutlineConfirm(outline) {
  if (!editor.taskId) return
  resumeBusy.value = true
  showOutline.value = false
  const ac = new AbortController()
  abortRef.value = ac
  try {
    const res = await streamConfirmOutline({
      taskId: editor.taskId,
      editedOutline: outline,
      signal: ac.signal,
    })
    await consumeStream(res, null)
  } catch (e) {
    if (e.name !== 'AbortError') message.error(e.message || '确认大纲失败')
    showOutline.value = true
  } finally {
    resumeBusy.value = false
    abortRef.value = null
  }
}
</script>

<template>
  <div class="page-editor">
    <header class="page-editor__hero">
      <h1 class="app-display-hero">创作工作台</h1>
      <p class="page-editor__lead">
        全流程 AI 驱动创作，从灵感到成稿，只需轻轻一触。
      </p>
    </header>

    <div class="page-editor__steps-wrapper">
      <a-steps :current="Math.min(stepIndex, 4)" :items="steps" class="page-editor__steps" />
    </div>

    <div class="page-editor__grid">
      <div class="page-editor__col">
        <div class="page-editor__card app-card">
          <TopicInput v-model:topic="topic" :disabled="streaming || resumeBusy" />
          <div class="page-editor__image-section">
            <span class="page-editor__label">配图策略</span>
            <ImageSelector v-model="imageSource" :disabled="streaming || resumeBusy" />
          </div>
          <div class="page-editor__actions">
            <button
              class="app-btn-warm"
              style="min-width: 180px"
              :disabled="!canStart || streaming"
              @click="onStart"
            >
              <template v-if="streaming">
                <a-spin size="small" style="margin-right: 8px" />
                正在创作中
              </template>
              <template v-else>开始创作之旅</template>
            </button>
            <button class="app-btn-pill-white" :disabled="!streaming" @click="onCancel">
              停止生成
            </button>
          </div>
        </div>

        <transition name="slide-fade">
          <div v-if="showTitle || showOutline" class="page-editor__interaction mt-32">
            <TitleSelector
              v-if="showTitle"
              :titles="titles"
              :loading="resumeBusy"
              @confirm="onTitleConfirm"
            />

            <OutlineEditor
              v-if="showOutline"
              :outline="outlineDraft"
              :loading="resumeBusy"
              @confirm="onOutlineConfirm"
            />
          </div>
        </transition>
      </div>
      <div class="page-editor__col">
        <ContentPreview :markdown="contentMd" />
      </div>
    </div>

    <div class="mt-48">
      <SSEViewer :lines="sseLines" />
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-editor {
  animation: pageFadeIn 1s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes pageFadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-editor__hero {
  margin-bottom: 60px;
  text-align: center;
}

.page-editor__lead {
  max-width: 800px;
  margin: 20px auto 0;
  font-size: 1.5rem;
  line-height: 1.6;
  font-weight: 300;
  color: $color-text-muted;
}

.page-editor__steps-wrapper {
  max-width: 1000px;
  margin: 0 auto 60px;
}

:deep(.ant-steps) {
  .ant-steps-item-title {
    font-family: $font-display;
    font-weight: 300;
    font-size: 16px !important;
    color: $color-text-muted !important;
    letter-spacing: 0.05em;
  }
  
  .ant-steps-item-active .ant-steps-item-title {
    color: $color-black !important;
    font-weight: 500;
  }

  .ant-steps-item-icon {
    background: transparent !important;
    border-color: $color-border !important;
    width: 32px;
    height: 32px;
    line-height: 30px;
    .ant-steps-icon { color: $color-text-muted; }
  }

  .ant-steps-item-finish .ant-steps-item-icon {
    border-color: $color-black !important;
    .ant-steps-icon { color: $color-black; }
  }
  
  .ant-steps-item-active .ant-steps-item-icon {
    background: $color-black !important;
    border-color: $color-black !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    .ant-steps-icon { color: $color-white; }
  }
  
  .ant-steps-item-tail::after {
    background-color: $color-border-subtle !important;
    height: 1px !important;
  }
}

.page-editor__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: start;
}

@media (max-width: 1280px) {
  .page-editor__grid {
    grid-template-columns: 1fr;
  }
}

.page-editor__card {
  padding: 48px;
}

.page-editor__image-section {
  margin-top: 32px;
}

.page-editor__label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: $color-text-muted;
  margin-bottom: 16px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.page-editor__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 40px;
  border-top: 1px solid rgba(0, 0, 0, 0.03);
  padding-top: 32px;
}

.mt-32 { margin-top: 32px; }
.mt-48 { margin-top: 48px; }

.slide-fade-enter-active {
  transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 1, 1);
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(30px);
  opacity: 0;
}
</style>
