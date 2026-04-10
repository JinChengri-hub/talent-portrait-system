#!/bin/bash
echo "=== 启动人才画像系统 ==="

# 启动后端
echo "[1/2] 启动 FastAPI 后端..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 启动前端
echo "[2/2] 启动 Vue3 前端..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✓ 后端运行中: http://localhost:8000"
echo "✓ 前端运行中: http://localhost:5173"
echo "✓ API 文档:   http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
