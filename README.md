# 尚图工坊

尚图工坊是一个面向中文电商团队的图文视频素材生产平台。当前仓库采用单仓结构，包含前端 React + Ant Design、后端 FastAPI + SQLAlchemy、任务队列 Celery + Redis，以及 Docker Compose 部署资产。

## 仓库结构

```text
backend/   后端 API、数据库模型、CLI、Celery Worker
frontend/  React 前端
deploy/    Docker Compose、Nginx、部署脚本
PLAN.md    项目总纲与完整设计文档
```

## 本地开发

### 1. 准备环境变量

从根目录复制一份环境变量文件：

```powershell
Copy-Item .env.example .env
```

必须至少检查以下变量：

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_EMAIL`
- `OPENAI_API_KEY`
- `MATTING_API_URL`
- `MATTING_API_KEY`

### 2. 初始化后端依赖

```powershell
cd backend
uv sync --dev
```

### 3. 初始化数据库与系统管理员

```powershell
uv run python -m app.cli init-db
```

这里会执行两件事：

1. 按当前 SQLAlchemy 元数据创建数据库表。
2. 读取根目录 `.env` 中的 `ADMIN_USERNAME`、`ADMIN_PASSWORD`、`ADMIN_EMAIL`，仅在数据库里还不存在该用户名时创建系统管理员。

特别注意：

- 管理员不会在每次应用启动时自动覆盖。
- 如果你修改了 `.env` 里的管理员密码，已经创建过的管理员不会被自动更新。
- 想调整管理员密码时，请走数据库或后台重置流程，不要误以为改 `.env` 就会生效。

### 4. 启动后端

```powershell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. 启动前端

```powershell
cd ../frontend
npm install
npm run dev
```

前端开发服务器默认通过 Vite 代理把 `/api` 转发到 `http://127.0.0.1:8000`。

## 测试与构建

### 后端测试

```powershell
cd backend
uv run pytest tests/test_billing.py tests/test_bootstrap.py tests/test_api_flow.py -q
```

### 前端测试

```powershell
cd frontend
npm test
```

### 前端构建

```powershell
cd frontend
npm run build
```

## 当前已打通的主链路

- 用户注册并创建工作区
- 用户登录
- 系统管理员登录
- 管理员创建充值卡批次
- 工作区兑换充值卡
- 商品创建
- PromptDraft 编译
- 价格预估
- 任务创建与积分冻结
- 前端总览、商品工作台、积分中心、管理员充值卡页面

## Docker Compose 部署

### 1. 服务器准备

目标服务器：`root@192.168.3.5`

需要已安装：

- Docker
- Docker Compose

### 2. 上传代码并准备 `.env`

在服务器项目根目录放置 `.env`，内容参考 `.env.example`。

### 3. 启动服务

```sh
cd deploy
docker compose up -d --build
```

或直接执行：

```sh
sh deploy/scripts/deploy.sh
```

### 4. 验证

- `http://服务器IP/api/health`
- 打开首页
- 注册新账号并创建工作区
- 用系统管理员登录创建充值卡
- 普通工作区兑换并创建商品任务

## 第三方服务说明

### OpenAI

当前默认用于：

- 文案生成
- 图片生成
- 视频生成

如果未配置 `OPENAI_API_KEY`，真实 AI 任务执行器暂时只能保持代码和部署就绪，不能在生产链路中调用第三方能力。

### 抠图服务

抠图采用独立 Provider，通过：

- `MATTING_API_URL`
- `MATTING_API_KEY`

进行接入。

### COS

当前仓库已预留 COS 变量，但开发态默认未接入真实 COS 上传链路，后续可继续把资产服务替换为正式 COS 实现。
