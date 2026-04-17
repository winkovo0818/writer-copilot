# AI 创作副驾驶 — 前端开发任务表

| 字段 | 值 |
|------|-----|
| 项目代号 | creator-copilot |
| 前端框架 | Vue 3 + Vite + Ant Design Vue + Pinia |
| 版本 | 1.0.0 |
| 创建日期 | 2026-04-17 |
| 状态 | 规划中 |

---

## 1. 前端架构概览

### 1.1 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 | 3.4+ |
| 构建 | Vite | 5.0+ |
| UI 库 | Ant Design Vue | 4.x |
| 状态管理 | Pinia | 2.x |
| 路由 | Vue Router | 4.x |
| HTTP | Axios | 1.6+ |
| 样式 | CSS / SCSS | - |
| 图表 | ECharts | 5.x |
| 图谱可视化 | D3.js | 7.x |

### 1.2 页面结构

```
frontend/src/
├── views/
│   ├── Editor.vue              # 创作工作台（核心）
│   ├── Knowledge.vue           # 知识库管理
│   ├── Graph.vue              # 知识图谱可视化
│   ├── StyleReport.vue        # 风格报告
│   ├── Matrix.vue             # 内容矩阵
│   ├── Dashboard.vue          # 数据看板
│   └── Settings.vue           # 设置
├── components/
│   ├── editor/
│   │   ├── TopicInput.vue     # 选题输入
│   │   ├── TitleSelector.vue  # 标题选择器
│   │   ├── OutlineEditor.vue # 大纲编辑器
│   │   ├── ContentPreview.vue# 正文预览
│   │   └── ImageSelector.vue # 配图选择器
│   ├── knowledge/
│   │   ├── ArticleList.vue   # 文章列表
│   │   └── ArticleImport.vue # 文章导入
│   ├── graph/
│   │   └── GraphCanvas.vue   # 图谱画布
│   ├── matrix/
│   │   └── MatrixGantt.vue   # 矩阵甘特图
│   └── common/
│       ├── SSEViewer.vue      # SSE 流式输出查看器
│       └── Loading.vue       # 加载状态
├── stores/
│   ├── editor.js             # 创作状态
│   ├── knowledge.js          # 知识库状态
│   ├── user.js               # 用户状态
│   └── stats.js              # 统计数据
├── api/
│   ├── article.js            # 创作 API
│   ├── knowledge.js          # 知识库 API
│   ├── graph.js              # 知识图谱 API
│   ├── style.js              # 风格 API
│   ├── matrix.js             # 矩阵 API
│   └── feedback.js           # 反馈 API
└── router/
    └── index.js              # 路由配置
```

---

## 2. 任务清单

### 2.1 FE-Epic-1：项目骨架

| ID | 任务名称 | 优先级 | 估时 | 依赖 | 状态 |
|----|----------|--------|------|------|------|
| FE-M-001 | Vue 3 + Vite 项目初始化 | M | 1d | - | [ ] |
| FE-M-002 | Ant Design Vue 集成 | M | 0.5d | FE-M-001 | [ ] |
| FE-M-003 | Pinia 状态管理配置 | M | 0.5d | FE-M-001 | [ ] |
| FE-M-004 | Vue Router 路由配置 | M | 0.5d | FE-M-001 | [ ] |
| FE-M-005 | Axios 封装（API Client） | M | 1d | - | [ ] |
| FE-M-006 | 全局样式与主题配置 | M | 1d | FE-M-002 | [ ] |
| FE-M-007 | 布局组件（Header/Sidebar） | M | 1d | FE-M-002 | [ ] |

**FE-Epic-1 合计**：6d + 20% 缓冲 ≈ 7d（约 1 周）

---

### 2.2 FE-Epic-2：创作工作台

| ID | 任务名称 | 优先级 | 估时 | 依赖 | 状态 |
|----|----------|--------|------|------|------|
| FE-M-008 | 选题输入组件（TopicInput） | M | 1d | FE-M-001 | [ ] |
| FE-M-009 | 配图策略选择器 | M | 0.5d | FE-M-008 | [ ] |
| FE-M-010 | 创作进度可视化 | M | 2d | - | [ ] |
| FE-M-011 | 标题选择器卡片（TitleSelector） | M | 2d | - | [ ] |
| FE-M-012 | 大纲编辑器（OutlineEditor） | M | 3d | - | [ ] |
| FE-M-013 | 正文预览 + Markdown 渲染 | M | 2d | - | [ ] |
| FE-M-014 | SSE 流式输出查看器（SSEViewer） | M | 2d | - | [ ] |
| FE-M-015 | 创作历史记录 | S | 1d | - | [ ] |
| FE-S-016 | 一键发布公众号 | S | 3d | - | [ ] |

**FE-Epic-2 合计**：16.5d + 20% 缓冲 ≈ 20d（约 3 周）

---

### 2.3 FE-Epic-3：知识库管理

| ID | 任务名称 | 优先级 | 估时 | 依赖 | 状态 |
|----|----------|--------|------|------|------|
| FE-M-017 | 文章列表页（ArticleList） | M | 2d | FE-M-001 | [ ] |
| FE-M-018 | 单篇导入表单（ArticleImport） | M | 1d | - | [ ] |
| FE-M-019 | 批量导入（支持 JSON/MD zip） | M | 2d | FE-M-018 | [ ] |
| FE-M-020 | 语义检索界面 | M | 2d | - | [ ] |
| FE-M-021 | 文章详情/预览 | M | 1d | FE-M-017 | [ ] |
| FE-S-022 | 文章标签管理 | S | 1d | FE-M-017 | [ ] |

**FE-Epic-3 合计**：9d + 20% 缓冲 ≈ 11d（约 1.5 周）

---

### 2.4 FE-Epic-4：知识图谱可视化

| ID | 任务名称 | 优先级 | 估时 | 依赖 | 状态 |
|----|----------|--------|------|------|------|
| FE-M-023 | D3.js 图谱画布（GraphCanvas） | M | 4d | - | [ ] |
| FE-M-024 | 节点交互（点击/拖拽/缩放） | M | 2d | FE-M-023 | [ ] |
| FE-M-025 | 概念详情面板 | M | 1d | FE-M-023 | [ ] |
| FE-C-026 | Gap 可视化高亮 | C | 2d | FE-M-023 | [ ] |
| FE-C-027 | 图谱导出（PNG/SVG） | C | 1d | FE-M-023 | [ ] |

**FE-Epic-4 合计**：10d + 20% 缓冲 ≈ 12d（约 1.5 周）

---

### 2.5 FE-Epic-5：风格报告

| ID | 任务名称 | 优先级 | 估时 | 依赖 | 状态 |
|----|----------|--------|------|------|------|
| FE-M-028 | 风格快照可视化 | M | 2d | - | [ ] |
| FE-M-029 | 月度报告页面 | M | 3d | - | [ ] |
| FE-M-030 | 漂移预警可视化 | M | 2d | - | [ ] |
| FE-M-031 | 风格基线对比 | M | 1d | FE-M-028 | [ ] |
| FE-S-032 | 雷达图展示多维风格 | S | 1d | FE-M-028 | [ ] |

**FE-Epic-5 合计**：9d + 20% 缓冲 ≈ 11d（约 1.5 周）

---

### 2.6 FE-Epic-6：内容矩阵

| ID | 任务名称 | 优先级 | 估时 | 依赖 | 状态 |
|----|----------|--------|------|------|------|
| FE-M-033 | 矩阵列表页 | M | 1d | - | [ ] |
| FE-M-034 | 矩阵详情页 | M | 2d | - | [ ] |
| FE-M-035 | 矩阵甘特图（MatrixGantt） | M | 3d | - | [ ] |
| FE-M-036 | 文章规划编辑 | M | 2d | FE-M-034 | [ ] |
| FE-S-037 | 发布节奏日历 | S | 2d | FE-M-034 | [ ] |
| FE-C-038 | 系列模板库 | C | 3d | FE-M-033 | [ ] |

**FE-Epic-6 合计**：13d + 20% 缓冲 ≈ 16d（约 2 周）

---

### 2.7 FE-Epic-7：数据看板

| ID | 任务名称 | 优先级 | 估时 | 依赖 | 状态 |
|----|----------|--------|------|------|------|
| FE-M-039 | 本月数据汇总卡片 | M | 1d | - | [ ] |
| FE-M-040 | 趋势图（ECharts 折线图） | M | 2d | - | [ ] |
| FE-M-041 | 爆款文章 TOP 排行 | M | 1d | - | [ ] |
| FE-M-042 | AI 洞察卡片 | M | 1d | - | [ ] |
| FE-M-043 | 数据导出 CSV | S | 1d | FE-M-039 | [ ] |
| FE-S-044 | 趋势对比（周/月/年） | S | 1d | FE-M-040 | [ ] |

**FE-Epic-7 合计**：7d + 20% 缓冲 ≈ 8d（约 1 周）

---

### 2.8 FE-Epic-8：LLM 监控面板

| ID | 任务名称 | 优先级 | 估时 | 依赖 | 状态 |
|----|----------|--------|------|------|------|
| FE-S-045 | 成本趋势图 | S | 2d | - | [ ] |
| FE-S-046 | 各模型调用占比饼图 | S | 1d | - | [ ] |
| FE-S-047 | 降级次数/失败率 | S | 1d | - | [ ] |
| FE-S-048 | Top 消费任务列表 | S | 1d | - | [ ] |

**FE-Epic-8 合计**：5d + 20% 缓冲 ≈ 6d（约 1 周）

---

## 3. 任务统计汇总

| Epic | Must | Should | Could | 合计 |
|------|------|--------|-------|------|
| FE-Epic-1 项目骨架 | 7 | 0 | 0 | 7 |
| FE-Epic-2 创作工作台 | 8 | 1 | 0 | 9 |
| FE-Epic-3 知识库管理 | 6 | 1 | 0 | 7 |
| FE-Epic-4 知识图谱 | 5 | 0 | 2 | 7 |
| FE-Epic-5 风格报告 | 5 | 1 | 0 | 6 |
| FE-Epic-6 内容矩阵 | 6 | 1 | 1 | 8 |
| FE-Epic-7 数据看板 | 5 | 1 | 0 | 6 |
| FE-Epic-8 LLM 监控 | 0 | 4 | 0 | 4 |
| **总计** | **42** | **9** | **3** | **54** |

---

## 4. 关键依赖路径

```
FE-M-001（项目骨架）
    └── FE-M-002（UI 库）
         └── FE-M-007（布局）
              ├── FE-Epic-2（创作工作台）
              │    └── FE-M-011/012/013/014
              ├── FE-Epic-3（知识库）
              ├── FE-Epic-4（图谱）
              ├── FE-Epic-5（风格）
              ├── FE-Epic-6（矩阵）
              ├── FE-Epic-7（看板）
              └── FE-Epic-8（LLM 监控）
```

---

## 5. 排期建议

### 5.1 前后端并行开发

后端 V0.1-V2.0 开发期间，前端可同步开始 FE-Epic-1。

### 5.2 前端开发时间线

| 阶段 | 任务 | 时间 |
|------|------|------|
| 第一周 | FE-Epic-1 项目骨架 | 1 周 |
| 第二周 | FE-Epic-2 创作工作台（基础） | 1.5 周 |
| 第三周 | FE-Epic-2 创作工作台（完善） | 1.5 周 |
| 第四周 | FE-Epic-3 知识库 + FE-Epic-4 图谱 | 1.5 周 |
| 第五周 | FE-Epic-5 风格 + FE-Epic-6 矩阵 | 1.5 周 |
| 第六周 | FE-Epic-7 看板 + FE-Epic-8 监控 + 收尾 | 1.5 周 |

**前端开发合计**：约 6-8 周

### 5.3 前后端对接

| 后端版本 | 前端对应 | 主要对接 |
|----------|---------|----------|
| V0.1 | FE-M-001~007 | API 基础 + SSE 调试 |
| V1.0 | FE-M-017~020 | 知识库管理 |
| V2.0 | FE-M-008~014 | 创作工作台 |
| V3.0 | FE-M-045~048 | LLM 监控 |
| V4.0 | FE-M-023~026 | 知识图谱 |
| V5.0 | FE-M-039~044 | 数据看板 |
| V6.0 | FE-M-028~032 | 风格报告 |
| V7.0 | FE-M-033~038 | 内容矩阵 |

---

## 6. 验收标准

### 6.1 性能要求

| 指标 | 目标 |
|------|------|
| 首屏加载 | < 2s |
| API 响应渲染 | < 500ms |
| SSE 流式渲染 | < 100ms 每 token |
| 图谱渲染（100 节点） | < 1s |

### 6.2 兼容性要求

- Chrome 90+
- Firefox 90+
- Safari 14+
- Edge 90+

### 6.3 响应式要求

- Desktop（≥ 1280px）：完整布局
- Tablet（768-1279px）：简化布局
- Mobile（< 768px）：基础移动端支持（创作工作台优先）

---

## 7. 技术规范

### 7.1 代码规范

- Vue 3 Composition API
- TypeScript（可选，建议使用）
- ESLint + Prettier
- 组件 ≤ 500 行
- 样式使用 SCSS + BEM 命名

### 7.2 状态管理规范

```javascript
// 使用 Pinia store
export const useEditorStore = defineStore('editor', {
  state: () => ({
    taskId: null,
    topic: '',
    status: 'idle',
  }),
  actions: {
    async startWriting(topic) { ... }
  },
})
```

### 7.3 API 调用规范

```javascript
// 统一使用封装好的 API client
import { articleApi } from '@/api/article'

// 创作任务
const task = await articleApi.createStream({ topic: 'xxx' })

// SSE 监听
task.on('content', (data) => { ... })
```

---

**文档维护约定**：
- 每周五更新任务状态
- 任务变更必须更新本文档
- 完成后标记 [x]