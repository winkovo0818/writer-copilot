# LangGraph 工作流演进文档

| 字段 | 值 |
|------|-----|
| 版本 | 1.0.0 |
| 创建日期 | 2026-04-17 |
| 状态 | 规划中 |

---

## 1. 当前实现 vs LangGraph 原生设计

### 1.1 当前实现（简化版）

```
文件：
- app/workflow/state.py    # ArticleState 数据类
- app/workflow/nodes.py   # 独立 async 函数
- app/workflow/edges.py   # 独立条件函数
- app/api/article.py       # SSE 流式调用（手动编排）
```

**特点**：
- nodes/edges 是独立函数，不依赖 LangGraph API
- SSE 流在 `article.py` 中手动编排
- 人机协作简化为"直接选第一个"

### 1.2 LangGraph 原生设计（目标）

```
文件：
- app/workflow/graph.py    # Graph 定义 + compile
- app/workflow/state.py    # ArticleState TypedDict
- app/workflow/nodes.py    # LangGraph 节点
- app/workflow/edges.py    # LangGraph 条件边
- app/workflow/checkpoint.py # checkpoint 配置
- app/api/article.py        # 调用编译后的 graph
```

**特点**：
- 使用 `StateGraph` 构建工作流
- 支持 `interrupt` 人机协作
- 支持 `checkpoint` 断线恢复
- 支持 `stream` 模式输出

---

## 2. 演进阶段

### 2.1 Phase 1：接入 LangGraph StateGraph（最小改动）

**目标**：用 LangGraph 封装现有节点，保持 SSE 流式输出不变。

**改动文件**：

| 文件 | 改动内容 |
|------|----------|
| `app/workflow/graph.py` | **新增** - `ArticleWorkflow` 类，`compile()` 方法 |
| `app/workflow/state.py` | 修改 - `ArticleState` 改为 `TypedDict` + `add_state_fields` |
| `app/workflow/nodes.py` | 小改 - 移除 `state: dict` 参数注解，改为 `Annotated[dict, add_state_fields]` |
| `app/workflow/edges.py` | 小改 - 条件函数签名调整为 LangGraph 格式 |
| `app/api/article.py` | 修改 - 调用 `graph.stream()` 替代手动编排 |

**关键代码**：

```python
# app/workflow/graph.py（新增）
from langgraph.graph import StateGraph
from app.workflow.state import ArticleState
from app.workflow.nodes import analyze_node, title_node, outline_node, write_node, image_node
from app.workflow.edges import should_continue, should_interrupt_title, should_interrupt_outline


class ArticleWorkflow:
    """文章创作工作流"""

    def __init__(self, checkpointer=None):
        self.graph = self._build_graph()
        self.checkpointer = checkpointer

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(ArticleState)

        # 添加节点
        workflow.add_node("analyze", analyze_node)
        workflow.add_node("title", title_node)
        workflow.add_node("outline", outline_node)
        workflow.add_node("write", write_node)
        workflow.add_node("image", image_node)

        # 设置入口
        workflow.set_entry_point("analyze")

        # 边
        workflow.add_edge("analyze", "title")
        workflow.add_edge("title", "outline")
        workflow.add_edge("outline", "write")
        workflow.add_edge("write", "image")
        workflow.add_edge("image", "__end__")

        return workflow.compile()

    def stream(self, input_state: dict, config: dict | None = None):
        """流式执行"""
        return self.graph.stream(input_state, config=config)


# app/workflow/state.py（修改）
from typing import TypedDict, Annotated
from langgraph.graph import add_state_fields


class ArticleState(TypedDict):
    """创作工作流状态"""
    task_id: str
    topic: str
    # ... 其他字段 ...
    current_node: str
    history: list[str]


# app/api/article.py（修改）
from app.workflow.graph import ArticleWorkflow

workflow = ArticleWorkflow()

@app.post("/article/stream")
async def create_article_stream(topic: str, ...):
    initial_state = {"task_id": str(uuid.uuid4()), "topic": topic, ...}

    # 使用 LangGraph 的 stream 模式
    config = {"configurable": {"thread_id": task_id}}
    generator = workflow.stream(initial_state, config)

    async def stream_response():
        async for chunk in generator:
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(stream_response(), ...)
```

---

### 2.2 Phase 2：启用 interrupt 人机协作

**目标**：标题和大纲阶段真正支持用户确认，而非自动选择第一个。

**改动文件**：

| 文件 | 改动内容 |
|------|----------|
| `app/workflow/graph.py` | 修改 - 添加 `interrupt_before` 配置 |
| `app/workflow/edges.py` | 修改 - `should_interrupt_title/outline` 返回 interrupt 指令 |
| `app/workflow/checkpoint.py` | **新增** - checkpoint 持久化配置 |
| `app/api/article.py` | 修改 - `/confirm-title` 接口恢复 workflow 执行 |

**关键代码**：

```python
# app/workflow/graph.py（修改）
def _build_graph(self) -> StateGraph:
    workflow = StateGraph(ArticleState)

    # ... 添加节点 ...

    # 标题后中断等待确认
    workflow.add_conditional_edges(
        "title",
        should_interrupt_title,
        {
            "continue": "outline",
            "interrupt": "__interrupt__"  # 暂停
        }
    )

    # 大纲后中断等待确认
    workflow.add_conditional_edges(
        "outline",
        should_interrupt_outline,
        {
            "continue": "write",
            "interrupt": "__interrupt__"
        }
    )

    return workflow.compile(checkpointer=self.checkpointer)


# app/workflow/edges.py（修改）
from typing import Literal


def should_interrupt_title(state: ArticleState) -> Literal["continue", "interrupt"]:
    """标题阶段是否中断"""
    if state.get("selected_title_id") is not None or state.get("edited_title"):
        return "continue"  # 用户已确认
    return "interrupt"  # 等待用户确认


def should_interrupt_outline(state: ArticleState) -> Literal["continue", "interrupt"]:
    """大纲阶段是否中断"""
    if state.get("edited_outline"):
        return "continue"
    return "interrupt"


# app/api/article.py（修改）
from langgraph.constants import END

workflow = ArticleWorkflow(checkpointer=checkpoint_saver)


@app.post("/article/confirm-title")
async def confirm_title(task_id: str, selected_id: int | None = None, edited_title: str | None = None):
    """确认标题后恢复 workflow"""
    config = {"configurable": {"thread_id": task_id}}

    # 更新 state
    update = {"selected_title_id": selected_id, "edited_title": edited_title}

    # 从中断点恢复
    result = workflow.invoke(None, config={**config, "resume": True})

    # 返回后续 SSE
    return stream_result(result)


@app.post("/article/confirm-outline")
async def confirm_outline(task_id: str, edited_outline: dict):
    config = {"configurable": {"thread_id": task_id}}
    update = {"edited_outline": edited_outline}

    result = workflow.invoke(None, config={**config, "resume": True})

    return stream_result(result)
```

---

### 2.3 Phase 3：多 Agent 协作增强

**目标**：支持 Sub-Graph，例如矩阵规划、反馈分析作为独立子工作流。

**改动文件**：

| 文件 | 改动内容 |
|------|----------|
| `app/workflow/matrix_graph.py` | **新增** - 矩阵规划子工作流 |
| `app/workflow/feedback_graph.py` | **新增** - 反馈分析子工作流 |
| `app/workflow/graph.py` | 修改 - 添加 `subgraphs` 配置 |
| `app/agents/matrix_planner.py` | 修改 - 支持作为子工作流调用 |
| `app/agents/feedback_analyzer.py` | 修改 - 支持作为子工作流调用 |

**关键代码**：

```python
# app/workflow/matrix_graph.py（新增）
from langgraph.graph import StateGraph, END


class MatrixPlanningState(TypedDict):
    """矩阵规划状态"""
    theme: str
    target_audience: str
    article_count: int
    articles: list[dict]  # 规划结果
    current_step: str


def planning_node(state: MatrixPlanningState) -> dict:
    # 调用 MatrixPlanner Agent
    ...


matrix_workflow = StateGraph(MatrixPlanningState)
matrix_workflow.add_node("planning", planning_node)
matrix_workflow.set_entry_point("planning")
matrix_workflow.add_edge("planning", END)
matrix_graph = matrix_workflow.compile()


# app/workflow/graph.py（修改）
from app.workflow.matrix_graph import matrix_graph


class ArticleWorkflow:
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(ArticleState)

        # ... 其他节点 ...

        # 矩阵规划（异步子工作流）
        workflow.add_node("matrix_plan", self._matrix_subgraph)

        return workflow.compile()

    async def _matrix_subgraph(self, state: ArticleState) -> dict:
        """调用矩阵规划子工作流"""
        matrix_input = {
            "theme": state.get("matrix_theme", ""),
            "target_audience": "技术开发者",
            "article_count": 8,
            "current_step": "start"
        }

        result = await matrix_graph.ainvoke(matrix_input)
        return {"matrix_plan": result}
```

---

### 2.4 Phase 4：流式输出优化

**目标**：正文写作节点真正实现 token 级流式 SSE 输出。

**改动文件**：

| 文件 | 改动内容 |
|------|----------|
| `app/workflow/nodes.py` | 修改 - `write_node` 返回异步生成器 |
| `app/workflow/graph.py` | 修改 - `stream` 模式支持 `stream_mode="custom"` |
| `app/api/article.py` | 修改 - SSE 输出适配 |

**关键代码**：

```python
# app/workflow/nodes.py（修改）
from typing import AsyncGenerator


async def write_node(state: ArticleState) -> AsyncGenerator[dict, None]:
    """流式写作节点 - yields 每个 token"""
    agent = ContentWriterAgent(llm=get_llm())

    async for chunk in agent.write_stream(context):
        # 每次 yielded 一个 chunk，更新 state
        yield {"content_chunk": chunk}

    # 完成后返回最终 state
    return {"content_status": "completed"}


# app/workflow/graph.py（修改）
from langgraph.graph import stream


def _build_graph(self) -> StateGraph:
    workflow = StateGraph(ArticleState)

    # 使用 custom stream mode
    workflow.add_node("write", write_node, stream=True)

    # ...

    return workflow.compile()


# app/api/article.py（修改）
@app.post("/article/stream")
async def create_article_stream(topic: str, ...):
    config = {
        "configurable": {"thread_id": task_id},
        "stream_mode": "custom"
    }

    async def stream_response():
        async for event in workflow.stream(initial_state, config):
            if "content_chunk" in event:
                # SSE 推送 token
                yield f"event: content\ndata: {event['content_chunk']}\n\n"
            elif "titles" in event:
                yield f"event: titles\ndata: {json.dumps(event['titles'])}\n\n"
            # ...

    return StreamingResponse(stream_response(), ...)
```

---

## 3. 文件改动总览

| 文件 | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|------|---------|---------|---------|---------|
| `app/workflow/graph.py` | **新增** | 修改 | 修改 | 修改 |
| `app/workflow/state.py` | 修改 | - | - | - |
| `app/workflow/nodes.py` | 小改 | - | - | 修改 |
| `app/workflow/edges.py` | 小改 | 修改 | - | - |
| `app/workflow/checkpoint.py` | - | **新增** | - | - |
| `app/workflow/matrix_graph.py` | - | - | **新增** | - |
| `app/workflow/feedback_graph.py` | - | - | **新增** | - |
| `app/api/article.py` | 修改 | 修改 | - | 修改 |
| `app/agents/matrix_planner.py` | - | - | 修改 | - |
| `app/agents/feedback_analyzer.py` | - | - | 修改 | - |

---

## 4. 依赖版本

```txt
# requirements.txt 需升级
langgraph >= 0.0.30  # 新版 interrupt API
langchain-core >= 0.1.0
```

---

## 5. 测试策略

| Phase | 测试重点 | 测试文件 |
|-------|---------|----------|
| Phase 1 | 工作流能完整执行 | `tests/unit/test_workflow_graph.py` |
| Phase 2 | interrupt 恢复正确 | `tests/unit/test_workflow_interrupt.py` |
| Phase 3 | 子工作流独立 + 集成 | `tests/unit/test_subgraph.py` |
| Phase 4 | 流式输出完整性 | `tests/integration/test_sse_stream.py` |

---

## 6. 风险与回退

| 风险 | 影响 | 回退方案 |
|------|------|----------|
| interrupt API 变更 | 编译失败 | 锁定 langgraph==0.0.29 |
| checkpoint 破坏现有逻辑 | 断线恢复失效 | Phase 1 先不加 checkpointer |
| 流式输出性能下降 | SSE 延迟增加 | 添加流式缓存 |

---

**维护约定**：每次改动后更新本文档版本号。
