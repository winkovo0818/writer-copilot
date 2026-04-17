# AI 创作副驾驶后端

## 技术栈

- **Web 框架**：FastAPI 0.109+
- **ORM**：SQLAlchemy 2.0（异步）
- **数据库**：SQLite（开发）/ MySQL（生产）
- **迁移**：Alembic
- **任务编排**：LangGraph
- **向量库**：Chroma
- **图数据库**：Neo4j
- **调度**：APScheduler

## 环境要求

- Python 3.11+
- Node.js 18+

## 本地开发

```bash
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 运行
uvicorn app.main:app --reload --port 8000

# 测试
pytest
```

## Docker 部署

```bash
docker-compose up -d
```

## 环境变量

参见 `.env.example`
