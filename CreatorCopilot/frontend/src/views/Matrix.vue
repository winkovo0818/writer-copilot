<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { matrixApi } from '@/api/matrix'
import MatrixGantt from '@/components/matrix/MatrixGantt.vue'

const list = ref([])
const loading = ref(false)
const selected = ref(null)
const detailLoading = ref(false)

const form = ref({
  name: '',
  theme: '',
  description: '',
  article_count: 8,
})

async function loadList() {
  loading.value = true
  try {
    const data = await matrixApi.list()
    list.value = data?.matrices || []
    if (list.value.length && !selected.value) {
      openDetail(list.value[0].matrix_id)
    }
  } catch (e) {
    message.error(e.message || '加载列表失败')
  } finally {
    loading.value = false
  }
}

async function openDetail(id) {
  detailLoading.value = true
  try {
    selected.value = await matrixApi.get(id)
  } catch (e) {
    message.error(e.message || '加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

async function createMatrix() {
  if (!form.value.name.trim() || !form.value.theme.trim()) {
    message.warning('请填写名称与主题')
    return
  }
  try {
    await matrixApi.create({
      name: form.value.name.trim(),
      theme: form.value.theme.trim(),
      description: form.value.description,
      article_count: form.value.article_count,
    })
    message.success('已创建')
    form.value = { name: '', theme: '', description: '', article_count: 8 }
    loadList()
  } catch (e) {
    message.error(e.message || '创建失败')
  }
}

onMounted(loadList)
</script>

<template>
  <div class="page-matrix">
    <header class="page-matrix__hero">
      <h1 class="app-display-hero">内容矩阵</h1>
      <p class="page-matrix__lead">系列规划、进度与甘特式排期示意。</p>
    </header>

    <div class="page-matrix__grid">
      <div class="app-card page-matrix__panel">
        <h3 class="page-matrix__h3">新建矩阵</h3>
        <a-form layout="vertical" @submit.prevent="createMatrix">
          <a-form-item label="名称" required>
            <a-input v-model:value="form.name" />
          </a-form-item>
          <a-form-item label="主题" required>
            <a-input v-model:value="form.theme" />
          </a-form-item>
          <a-form-item label="描述">
            <a-textarea v-model:value="form.description" :rows="2" />
          </a-form-item>
          <a-form-item label="计划篇数">
            <a-input-number v-model:value="form.article_count" :min="1" :max="64" />
          </a-form-item>
          <a-button type="primary" html-type="submit">创建</a-button>
        </a-form>
      </div>

      <div class="app-card page-matrix__panel">
        <h3 class="page-matrix__h3">矩阵列表</h3>
        <a-spin :spinning="loading">
          <a-list :data-source="list" item-layout="horizontal">
            <template #renderItem="{ item }">
              <a-list-item class="page-matrix__row" @click="openDetail(item.matrix_id)">
                <a-list-item-meta :title="item.name" :description="item.theme">
                  <template #avatar>
                    <a-progress
                      type="circle"
                      :percent="Math.round((item.progress || 0) * 100)"
                      :width="40"
                    />
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-spin>
      </div>
    </div>

    <a-spin :spinning="detailLoading">
      <div v-if="selected" class="app-card page-matrix__detail">
        <h3 class="page-matrix__h3">{{ selected.name }}</h3>
        <p class="app-muted">{{ selected.description }}</p>
        <MatrixGantt :articles="selected.articles || []" />
      </div>
    </a-spin>
  </div>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.page-matrix__hero {
  margin-bottom: 24px;
}

.page-matrix__lead {
  color: $color-text-secondary;
  max-width: 640px;
}

.page-matrix__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

@media (max-width: 960px) {
  .page-matrix__grid {
    grid-template-columns: 1fr;
  }
}

.page-matrix__panel {
  padding: 24px;
}

.page-matrix__h3 {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.75rem;
  margin: 0 0 16px;
}

.page-matrix__row {
  cursor: pointer;
}

.page-matrix__detail {
  margin-top: 24px;
  padding: 24px;
}
</style>
