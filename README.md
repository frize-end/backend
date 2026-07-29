# 资产管理后端系统
基于 FastAPI 开发的中小型资产管理后端，个人独立练习项目，主要实现硬件/物品资产台账与基础申领管理，用于后端技术实践与简历项目展示。

## 项目简介
本系统为单体架构后端，实现资产信息维护、人员权限管理、资产领用归还登记等基础功能。解决资产信息零散、领用记录无留存等基础管理场景需求。
项目重点实践 FastAPI 工程分层架构、ORM 数据操作、统一接口规范、RBAC基础权限控制等后端常用技术方案。

## 技术栈
- 后端框架：FastAPI
- ORM：SQLAlchemy 2.0
- 数据库：MySQL 8.0
- 环境配置：python-dotenv
- 代码规范：Ruff

> 可选扩展（当前版本未实现，仅作为后续优化方向）：Redis缓存、定时任务、消息通知

## 已实现功能模块
- 用户&权限模块：用户管理、角色划分、基础RBAC权限控制
- 资产台账模块：资产新增、编辑、分类管理、状态维护
- 资产流转模块：资产申领、归还记录登记
- 日志模块：关键操作简易记录
- 统一返回封装、全局异常捕获、请求参数校验

## 项目目录
```plaintext
FastAPI_Pro/
├── app/                    # 业务主目录
│   ├── main.py             # 项目启动入口
│   ├── api/                # 路由接口分层
│   ├── core/               # 全局配置、安全相关
│   └── common/             # 公共工具、响应模板、异常处理
├── .venv/                  # 本地虚拟环境（git忽略）
├── .env                    # 私有环境变量（git忽略）
├── .gitignore
├── requirements-base.txt   # 运行核心依赖
├── requirements-dev.txt    # 开发工具依赖
└── requirements-lock.txt   # 锁定依赖版本

```
## 本地运行
1. 创建虚拟环境
```bash
python -m venv .venv
2.激活环境
# Windows PowerShell
.venv\Scripts\Activate.ps1
3.安装依赖
# 开发环境
pip install -r requirements-base.txt -r requirements-dev.txt
# 生产环境
pip install -r requirements-lock.txt
4.启动服务
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
## 接口文档
Swagger 文档：http://127.0.0.1:8000/docs
ReDoc 文档：http://127.0.0.1:8000/redoc
## 开发规范
配置信息存放于 .env，禁止密钥硬编码提交代码仓库
代码遵循 Ruff 规范，保持统一编码风格
业务分层解耦，接口、数据模型、业务逻辑分离
## 项目收获
练习 FastAPI 标准化工程搭建、异步接口开发、数据库设计、权限体系落地，熟悉后端项目完整开发流程，掌握中小型单体后端项目结构设计思路。
