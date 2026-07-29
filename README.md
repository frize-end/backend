# 企业内部资源管理中台
## 环境搭建
1. 创建虚拟环境
python -m venv .venv
2. 激活虚拟环境
Windows Powershell: .venv\Scripts\Activate.ps1
3. 安装依赖
pip install -r requirements-base.txt
## 启动服务
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
## 接口文档
在线调试：http://127.0.0.1:8000/docs
