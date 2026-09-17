"""
仓库根目录引导文件
把 SnapDeploy 的启动重定向到 backend/app.py
"""
import sys
import os
import importlib.util

# backend 目录的绝对路径
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')

# 加入 Python 路径 + 切换工作目录
sys.path.insert(0, BACKEND_DIR)
os.chdir(BACKEND_DIR)

# 明确加载 backend/app.py，避免模块名冲突
spec = importlib.util.spec_from_file_location(
    "backend_app",
    os.path.join(BACKEND_DIR, "app.py")
)
backend_app = importlib.util.module_from_spec(spec)
sys.modules["backend_app"] = backend_app
spec.loader.exec_module(backend_app)

# 导出 app 给 gunicorn / flask 用
app = backend_app.app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
