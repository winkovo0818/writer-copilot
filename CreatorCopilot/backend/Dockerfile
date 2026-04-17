FROM python:3.11-slim

WORKDIR /app

# 依赖（含可选 Chroma 向量库）
COPY requirements.txt requirements-chroma.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-chroma.txt

# 代码
COPY . .

# 数据目录
RUN mkdir -p /app/data /app/data/logs /app/data/chroma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
