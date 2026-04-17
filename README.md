# Writer Copilot（Creator Copilot）

AI 辅助创作全栈项目：Vue 3 + Vite 前端，FastAPI + LangGraph 后端，支持知识库、矩阵规划、图谱与 LLM 编排等能力。

## 仓库结构

| 目录 | 说明 |
|------|------|
| `frontend/` | Web 前端（Vite、Vue 3、Ant Design Vue） |
| `backend/` | API 与任务编排（FastAPI、LangGraph 等） |
| `docs/` | 设计/演进类文档 |
| `scripts/` | 辅助脚本 |
| `docker-compose.yml` | 本地依赖与后端编排（Neo4j 等） |

更细的前端交互与视觉约定见 `frontend/DESIGN.md`。

## 环境要求

- **Python** 3.11+
- **Node.js** 18+
- 可选：**Docker**（Neo4j、后端容器化）

## 本地开发

### 1. 后端

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# 按需编辑 .env
uvicorn app.main:app --reload --port 8000
```

默认 API 地址：`http://127.0.0.1:8000`。环境变量说明见 `backend/.env.example`；后端更多说明见 `backend/README.md`。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

按 Vite 提示访问本地开发地址（一般为 `http://localhost:5173`）。请与后端 API 地址、代理配置保持一致（见 `frontend/vite.config.js` 等）。

### 3. 测试（后端）

```bash
cd backend
pytest
```

## Docker

在项目根目录：

```bash
docker compose up -d
```

将启动后端、Neo4j 等（端口见 `docker-compose.yml`）。若需调度任务 worker，可使用 profile：`docker compose --profile scheduler up -d`。

> 说明：根目录 `docker-compose.yml` 中包含前端服务构建配置；若本地尚未提供 `frontend/Dockerfile`，请先使用上面的「本地开发」方式运行前端，或自行补充镜像构建文件后再执行完整编排。

## 许可证

尚未包含 `LICENSE` 文件；若对外发布，请按需补充。
