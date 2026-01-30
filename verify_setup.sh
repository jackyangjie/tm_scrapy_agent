#!/bin/bash
set -e

echo "🔍 开始验证 FastAPI 后端设置..."
echo ""

# 1. 检查文件结构
echo "📁 验证文件结构..."
ls -la backend/api/
echo ""

# 2. 检查模型文件
echo "📊 验证数据模型..."
python -c "
import backend.models.schemas
print('数据模型导入测试通过')
" 2>&1 || echo "⚠️ 数据模型导入失败"

echo ""
echo "✅ 基础文件检查完成！"
echo ""

# 3. 检查依赖
echo "📦 检查 Python 依赖..."
python -c "
import sys
try:
    import fastapi, uvicorn
    print('✅ FastAPI 导入成功')
except ImportError as e:
    print(f'❌ 缺少依赖: {e}')
" 2>&1 || echo "⚠️ 某础依赖检查失败"

# 4. 验证 API 结构
echo ""
echo "📋 验证 API 结构..."
python -c "
import sys
sys.path.insert(0, './backend')
from api import chat_router, task_router
print('API 路由导入测试通过')
" 2>&1 || echo "⚠️ API 路由导入失败"

echo ""
echo "✅ 所有检查完成！"
echo ""

# 5. 生成测试命令
echo "🚀 测试命令："
echo "1. 启动服务:"
echo "   cd backend && python main.py"
echo ""
echo "2. 测试 API:"
echo "   curl http://localhost:8000/"
echo "   curl http://localhost:8000/health"
echo "   curl -X POST http://localhost:8000/api/chat/send -H \"Content-Type: application/json\" -d '{\"message\": \"测试\"}'"
echo ""

echo "📄 API 文档: http://localhost:8000/docs"
echo ""
echo "🎉 后端设置验证完成！"
echo ""
