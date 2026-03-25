# 尚图工坊｜项目总纲与完整开发设计文档

**版本**：0.1.0
**日期**：2026-03-25
**文档定位**：项目唯一主文档
**站点语言**：仅中文界面
**前端技术栈**：React + Ant Design
**后端技术栈**：FastAPI + SQLAlchemy 2.x + PostgreSQL + Celery + Redis + COS
**部署主方案**：Linux + Docker Compose
**计费体系**：整数积分；任务开始前展示预计扣费；采用冻结 -> 结算 -> 释放/退款；暂不接在线支付，仅支持管理员生成充值卡与后台调账
**目标平台**：Amazon、抖音小店

---

## 目录
1. 文档定位与项目定义
2. 产品目标、成功标准与非目标
3. 用户角色、权限与典型使用场景
4. 功能范围总览与边界
5. 核心设计原则与默认假设
6. 核心概念与业务对象
7. 全链路业务流程
8. 信息架构与页面方案
9. 技术栈与系统架构
10. 后端实施方案
11. 前端实施方案
12. 数据库设计
13. 配方系统、模型管理与路由策略
14. 积分、定价、充值卡与账本体系
15. 异步任务、SSE 与生成执行体系
16. 模板渲染、资产处理与 COS 方案
17. 管理后台与运营使用方案
18. 本地开发、部署与运维方案
19. 安全、合规、风控与观测
20. 测试策略与验收标准
21. 完整建设顺序与模块依赖
22. 风险边界与后续演进方向

---

## 1. 文档定位与项目定义

### 1.1 文档定位
本文件是“尚图工坊”项目的唯一主文档，同时承担以下职责：
- 项目立项与产品目标说明。
- 面向研发的系统架构与数据设计说明。
- 面向实施的开发、部署、运维与测试规范。
- 面向业务和运营的使用方案说明。

后续如产生更细粒度的专题文档，例如接口契约、数据库迁移说明、运营后台操作手册、部署 SOP，均应以本文件为上位依据，不得与本文件冲突。

### 1.2 项目定义
尚图工坊是一个面向电商卖家与电商团队的多租户 SaaS 素材生产平台，核心目标是围绕“同款一致性”建立标准化的商品素材生产流水线。系统以真实商品图片为基础，结合配方系统、模型路由、模板渲染、积分计费、版本追溯、任务队列和后台治理能力，提供图文视频一体化生产能力。

### 1.3 产品定位
产品定位不是“通用 AI 生图站”，而是“电商商品素材工厂”：
- 面向商品运营，不面向泛娱乐生成。
- 面向批量与复用，不是单次玩具式生成。
- 面向业务可交付，不是只追求模型演示效果。
- 面向企业内协作与审计，不是单用户创作工具。

### 1.4 商业场景
系统服务于以下典型对象：
- 跨境电商团队，为 Amazon 商品生产主图、场景图、尺寸图、详情图、文案与视频。
- 国内电商团队，为抖音小店等渠道生产场景图、卖点海报、短视频与详情页素材。
- 代运营、设计服务商，通过工作区机制同时服务多个客户或品牌。

---

## 2. 产品目标、成功标准与非目标

### 2.1 产品目标
围绕一个商品，提供从产品建档、图片上传、抠图、提示词编译、图文视频生成、迭代优化、导出交付到积分结算的完整闭环。

### 2.2 核心目标
- 为商品提供“同款一致性”的素材生产能力，确保主体不漂移、风格可复用、结果可追溯。
- 让非设计人员也能基于产品资料和结构化配置产出可用素材。
- 让团队能够批量管理配方、模板、模型、价格、积分和审计。
- 让运营和管理员可以在后台解释“为什么这样生成、为什么这样扣费、为什么任务失败”。

### 2.3 成功标准
项目上线后应满足以下标准：
- 用户能在单个工作区内完成从产品建档到导出的完整链路，无需线下拼接多个工具。
- 同一商品多轮生成仍能维持主体一致性和风格连续性。
- 所有任务在创建前都能展示可解释的预计扣费。
- 所有成功和失败的扣费结果都能在账本中追溯。
- 管理员能在后台调整配方、模型、价格、充值卡并使新任务即时生效。
- 生产环境部署、回滚、日志排查和数据库迁移具备可执行 SOP。

### 2.4 非目标
以下内容不属于当前正式建设范围：
- 在线支付接入，如微信支付、支付宝、支付回调、退款单据、发票体系。
- 对外开放 API 平台与第三方 SaaS 集成。
- 小程序、移动端 App、桌面客户端。
- 面向普通消费者的公开创作社区。
- 电商 ERP、订单履约、仓储物流等非素材生产领域功能。

---

## 3. 用户角色、权限与典型使用场景

### 3.1 角色定义
- **系统超级管理员（SystemAdmin）**：管理全站模型、路由、定价、充值卡批次、全局配方、全局模板、审计和异常补偿。
- **工作区 Owner**：管理工作区成员、品牌档案、充值卡兑换记录、积分流水、工作区内配方和模板。
- **工作区 Admin**：协助 Owner 管理产品、模板、配方、生成任务和成员。
- **Member**：创建产品、上传素材、发起生成、迭代优化、导出结果。
- **Viewer**：只读查看和下载授权范围内的结果，不发起生产任务。

### 3.2 权限边界
- 工作区是权限、资产、任务、积分和模板的隔离边界。
- 系统级配置只能由 SystemAdmin 修改。
- 工作区级模板、配方、品牌档案只能在所属工作区内可见和生效。
- Viewer 不可发起扣费动作。
- 所有涉及积分变动、价格调整、模型启停、充值卡发放、配方发布、模板发布、导出和后台调账的动作必须写入审计日志。

### 3.3 典型使用场景

#### 场景 A：运营成员生产商品图文视频
1. 进入所属工作区。
2. 新建商品并填写结构化信息。
3. 上传白底图、多角度图或参考图。
4. 等待系统完成缩略图、抠图与切图处理。
5. 选择平台方案、产物包、配方和控制项。
6. 查看系统编译出的提示词草稿和预计扣费。
7. 发起生成并实时查看任务状态。
8. 对某个结果执行继续优化、局部重绘、风格微调或设为风格锚点。
9. 批量导出图片、详情长图、文案和视频。

#### 场景 B：工作区管理员管理可复用生产规则
1. 创建或调整品牌档案。
2. 维护工作区自定义配方与模板。
3. 给不同商品类型设置常用产物包。
4. 查看本工作区积分流水、充值卡兑换记录、失败任务和导出记录。
5. 复盘哪个配方、哪个模型、哪个模板产出效果更稳定。

#### 场景 C：系统管理员治理全站平台能力
1. 配置 Provider Key 和模型目录。
2. 创建模型组与路由策略。
3. 发布价格方案和价格规则。
4. 生成充值卡批次并管理卡密状态。
5. 查看任务失败原因、队列堆积、模型错误率和账本异常。
6. 调整全局模板、全局配方、背景素材库和风控规则。

---

## 4. 功能范围总览与边界

### 4.1 当前正式范围
本项目当前总规划必须完整覆盖以下模块：
- 多租户工作区、用户、成员、RBAC、审计。
- 产品建档、品牌档案、平台方案、资产上传与处理。
- 配方系统、产物包、提示词草稿、AI 提示词优化。
- 图片、海报、详情长图、文案、视频生成。
- 继续优化、局部重绘、版本树、风格锚点。
- 模型管理、模型组、路由策略、降级策略、限流策略。
- 整数积分、价格规则、预计扣费、冻结结算释放、退款。
- 管理员生成充值卡、兑换充值卡、后台调账。
- 结果导出、批量压缩包导出、下载授权。
- 模板渲染、抠图、缩略图、背景素材库。
- Docker Compose 部署、运维、日志、监控和告警。

### 4.2 当前明确不做的内容
- 用户在线直接付款购买积分。
- 公开开放平台 API。
- 供应商财务分账或模型供应商自动结算。
- 原生移动端和小程序。
- 营销裂变、分销体系、客户对账单导出中心。

### 4.3 边界说明
当前不做在线支付，不代表账务体系可以简化。当前仍需完整建设：
- 钱包余额。
- 账本流水。
- 扣费预估。
- 扣费冻结与释放。
- 充值卡批次和卡密状态。
- 后台人工补偿和调整。

---

## 5. 核心设计原则与默认假设

### 5.1 核心设计原则
1. **同款一致性优先**：以真实商品图为主体来源，优先锁定主体，不允许生成结果偏离商品事实。
2. **模板渲染优先**：所有带文字的海报、尺寸图、参数图、详情长图必须通过后端模板系统渲染，不依赖模型画字。
3. **计费可解释可追溯**：每个最小任务单元都要记录定价快照、模型快照、执行参数快照。
4. **平台规则内建**：Amazon 与抖音不是 UI Tab，而是配方默认值、模板偏好、合规规则、推荐产物组合和视觉差异的集合。
5. **可降级交付**：第三方模型失败时，系统尽量以替代方案交付，而不是简单报错。
6. **后台治理优先**：所有关键能力必须可配置、可审计、可追溯、可回滚。
7. **完整建设，不做阉割版主流程**：不以 MVP 为目标，不通过砍掉核心模块换取“先跑起来”。

### 5.2 默认假设
- 产品面向中文运营团队，系统 UI 不做多语言。
- 前后端分离部署。
- 本地开发也以 PostgreSQL 为准，避免 SQLite 与生产行为偏差。
- 文件统一使用 UTF-8 编码。
- 生产环境对象存储采用腾讯云 COS 私有桶。
- 视频能力与图片能力同级纳入正式方案。

---

## 6. 核心概念与业务对象

- **Workspace**：多租户隔离边界，承载成员、产品、资产、任务、积分、品牌档案、模板、配方。
- **PlatformProfile**：平台方案，如 Amazon / Douyin，封装平台规则、默认配方、推荐产物、合规要求。
- **BrandProfile**：品牌档案，包含风格、人群、禁宣词、关键词、配色、视觉偏好、平台偏好。
- **Product**：商品档案，包含结构化事实信息、自由说明、资产集合、平台状态。
- **Asset**：系统内的文件资产，包括原图、cutout、mask、缩略图、输出结果、模板预览、导出包。
- **Recipe / RecipeVersion**：可执行配方及其版本，定义输入要求、提示词模板、输出规格、执行策略、定价标签和限制。
- **Pack**：产物包，一次性选择多个类别与数量的组合。
- **PromptDraft**：提示词草稿与编译结果，可编辑、优化、确认和版本化。
- **Job / JobItem**：一次生成任务与最小执行单元。
- **Generation**：最终产物记录，支持版本树和父子关系。
- **Provider / ProviderModel / ModelGroup / RoutingPolicy**：模型供应商、具体模型、模型组合和路由规则。
- **PricePlan / PriceRule**：价格方案和规则。
- **CreditWallet / CreditLedger**：积分钱包与流水账本。
- **RechargeCardBatch / RechargeCard / RechargeRedemption**：充值卡批次、卡密和兑换记录。

---

## 7. 全链路业务流程

### 7.1 工作区开通与积分准备
1. 系统管理员创建或开通工作区。
2. Owner/Admin 邀请成员加入工作区。
3. 系统管理员根据销售或内部安排生成充值卡批次。
4. 工作区管理员兑换充值卡，积分进入钱包并记录账本。
5. 工作区管理员开始配置品牌档案、模板和自定义配方。

### 7.2 产品建档与资产预处理
1. 创建产品。
2. 填写类目、材质、尺寸、卖点、禁宣信息、目标平台等结构化字段。
3. 上传白底图、多角度图、参考图。
4. 系统触发异步任务，完成缩略图、抠图、mask 生成、文件哈希和尺寸识别。
5. 当前端看到产品已具备 cutout/mask 后，允许进入正式生成。

### 7.3 平台选择与产物组合
1. 用户进入产品工作台。
2. 切换平台方案，平台方案带出推荐产物包和默认配方。
3. 用户选择产物包，或按分类勾选单项产物。
4. 用户为每个产物类别设置张数、比例、清晰度、风格、场景主题和控制项。

### 7.4 提示词草稿与生成确认
1. 系统读取产品事实、品牌档案、平台规则、配方版本和用户控制项。
2. 编译生成 PromptDraft。
3. 用户可在普通模式下只编辑控制项，也可在高级模式查看完整提示词。
4. 用户可发起“AI 优化提示词”，系统生成新的草稿版本但不得覆盖原始确认稿。
5. 用户点击“预计扣费”查看费用明细后再发起任务。

### 7.5 任务创建与计费
1. 前端调用价格预估接口。
2. 后端重新计算预估结果，防止前端篡改。
3. 校验余额是否足够。
4. 冻结任务所需积分。
5. 创建 Job 和多个 JobItem。
6. 各 JobItem 根据类型进入不同队列执行。

### 7.6 生成执行
- 图片类：背景生成、主体融合、阴影处理、局部修复、超分。
- 模板类：按模板 JSON 和业务数据后端渲染图片。
- 文案类：根据产品信息、平台规则和品牌调性生成标题、卖点、详情文案。
- 视频类：根据图片和脚本生成场景视频；失败时降级为关键帧动效视频。

### 7.7 结果查看与继续优化
1. 前端通过 SSE 接收任务状态。
2. 用户按分类查看结果流。
3. 用户对某张结果执行继续优化、只改背景、局部重绘、微调风格。
4. 系统生成新的 Generation，并保持版本树可追溯。

### 7.8 导出交付
1. 用户单张下载或批量导出。
2. 系统异步生成导出包并上传 COS。
3. 返回短期签名下载地址。
4. 审计系统记录导出行为。

### 7.9 管理员运营闭环
1. 查看失败任务、扣费异常、充值卡兑换异常。
2. 对失败任务进行补偿或退款。
3. 调整价格策略、模型组、路由规则和风控规则。
4. 持续优化全局模板、全局配方和背景素材库。

---

## 8. 信息架构与页面方案

### 8.1 顶层导航
- 登录页
- 工作区选择页
- 产品中心
- 产品工作台
- 配方中心
- 产物包中心
- 模板中心
- 品牌档案
- 积分中心
- 导出记录
- 系统管理后台

### 8.2 产品工作台
产品工作台是系统核心页面，应包含四大区域：
- 左侧：产品资料、资产状态、平台规则提示、品牌档案摘要。
- 中间：产物包选择、分类配置、控制项面板。
- 右侧：PromptDraft、高级设置、预计扣费、任务提交区。
- 底部：生成结果流、版本树、继续优化、下载和收藏操作。

### 8.3 管理后台信息架构
- Provider 管理
- 模型目录
- 模型组与路由
- 价格方案与规则
- 充值卡批次与卡密管理
- 全局配方与模板
- 背景素材库
- 审计日志
- 全站任务监控
- 全站钱包与异常流水

### 8.4 运营使用方案
管理后台不只是配置清单，还必须支持以下运营动作：
- 快速定位失败任务的具体失败点。
- 查看某个工作区最近的生成量、失败率、扣费情况。
- 查看某张图使用了哪个配方、哪个模型、哪个价格规则。
- 对某个工作区追加积分或退款补偿。
- 作废某批充值卡、冻结风险工作区、停用异常模型。

---

## 9. 技术栈与系统架构

### 9.1 技术栈选择
- 后端：FastAPI
  - 适合高并发 API、类型约束、异步场景、SSE 推送和后台接口统一管理。
- ORM：SQLAlchemy 2.x
  - 便于模型层、事务控制、迁移配合和复杂查询组织。
- 数据库：PostgreSQL
  - 适合 JSONB、GIN 索引、事务账本、复杂后台查询和扩展。
- 驱动：psycopg3 为主，异步链路按 SQLAlchemy 官方兼容方式组织。
- 异步任务：Celery + Redis
  - 支撑生成、抠图、导出、模板渲染和文案任务解耦。
- 前端：React + Ant Design
  - 适合复杂后台、表单、管理配置、工作台交互和中文业务系统。
- 存储：腾讯云 COS
  - 管理原图、抠图、生成结果、模板预览、导出包。
- 反向代理：Nginx
  - 负责 HTTPS、前端静态资源、API 转发、SSE 透传和大文件上传控制。

### 9.2 系统服务划分
- `web-frontend`：React 构建产物，由 Nginx 托管。
- `api-server`：FastAPI 主应用。
- `worker-default`：Celery 默认任务执行器。
- `worker-video`：视频相关高耗时任务执行器。
- `redis`：Broker、缓存、PubSub、限流信号量。
- `postgres`：业务数据库。
- `nginx`：反向代理、静态资源服务和网关。

### 9.3 逻辑分层
- 接入层：HTTP API、鉴权、参数校验、统一响应、SSE。
- 领域层：产品、任务、定价、账本、模板、配方、路由、充值卡等核心业务。
- 基础设施层：数据库、Redis、COS、第三方模型 Provider、日志监控。
- 异步执行层：Celery Worker、导出处理、图片视频流水线、文案生成。

### 9.4 推荐仓库结构
```text
shangtugongfang/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ core/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  ├─ repositories/
│  │  ├─ workers/
│  │  └─ templates/
│  ├─ migrations/
│  ├─ tests/
│  └─ pyproject.toml
├─ frontend/
│  ├─ src/
│  │  ├─ app/
│  │  ├─ pages/
│  │  ├─ components/
│  │  ├─ features/
│  │  ├─ services/
│  │  ├─ hooks/
│  │  └─ styles/
│  ├─ public/
│  └─ package.json
├─ deploy/
│  ├─ docker-compose.yml
│  ├─ nginx/
│  └─ scripts/
├─ docs/
└─ PLAN.md
```

---

## 10. 后端实施方案

### 10.1 模块划分
- `auth`：登录、刷新、当前用户、权限判断。
- `workspace`：工作区、成员、角色、邀请。
- `product`：商品档案、品牌档案、平台状态。
- `asset`：上传记录、COS key、下载签名、预处理状态。
- `recipe`：配方、版本、产物包、提示词草稿。
- `generation`：任务、结果、版本树、继续优化。
- `billing`：钱包、账本、价格规则、价格估算、充值卡、调账。
- `provider`：Provider、模型、模型组、路由、健康检查。
- `admin`：全站后台配置和监控。
- `audit`：审计日志查询和写入。

### 10.2 API 统一约定
- Base Path：`/api`
- 统一响应：
```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```
- 鉴权：JWT Access + Refresh
- 时间字段统一为 ISO 8601
- 列表接口统一支持分页、筛选、排序
- 所有工作区资源接口必须校验当前工作区归属

### 10.3 关键用户端接口
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/me`
- `GET /api/workspaces`
- `POST /api/workspaces`
- `POST /api/workspaces/{id}/members/invite`
- `POST /api/uploads/cos/credentials`
- `POST /api/assets/record`
- `GET /api/assets/{id}/download-url`
- `POST /api/products`
- `GET /api/products`
- `GET /api/products/{id}`
- `PATCH /api/products/{id}`
- `POST /api/prompt-drafts/compile`
- `PATCH /api/prompt-drafts/{id}`
- `POST /api/prompt-drafts/{id}/improve`
- `POST /api/pricing/estimate`
- `POST /api/jobs`
- `GET /api/jobs/{id}`
- `GET /api/jobs/{id}/items`
- `GET /api/jobs/{id}/events`
- `POST /api/generations/{id}/iterate`
- `POST /api/exports/zip`
- `GET /api/credits/balance`
- `GET /api/credits/ledger`
- `POST /api/credits/recharge-cards/redeem`

### 10.4 关键管理端接口
- `GET /api/admin/providers`
- `GET /api/admin/provider-models`
- `GET /api/admin/model-groups`
- `GET /api/admin/routing-policies`
- `GET /api/admin/price-plans`
- `GET /api/admin/price-rules`
- `GET /api/admin/recharge-card-batches`
- `POST /api/admin/recharge-card-batches`
- `GET /api/admin/recharge-cards`
- `POST /api/admin/credits/adjust`
- `GET /api/admin/audit-logs`
- `GET /api/admin/jobs/overview`

### 10.5 编码与事务要求
- 账本相关写操作必须以事务完成。
- 对 `hold/capture/release/refund` 采用幂等键防重复入账。
- 关键动作先写审计再返回成功。
- 任务状态写库与 Redis 发布必须保证顺序一致。

---

## 11. 前端实施方案

### 11.1 页面结构
- `/login`
- `/workspaces`
- `/products`
- `/products/new`
- `/products/:id`
- `/recipes`
- `/packs`
- `/templates`
- `/brand-profiles`
- `/credits`
- `/exports`
- `/admin/providers`
- `/admin/models`
- `/admin/routing`
- `/admin/pricing`
- `/admin/recharge-cards`
- `/admin/audit-logs`
- `/admin/jobs`

### 11.2 状态管理建议
- 页面级表单状态以 React 组件状态为主。
- 跨页面用户态、工作区态、权限态、基础字典和筛选条件采用集中状态管理。
- 服务端状态建议通过统一请求层 + 缓存查询方案管理。
- SSE 事件通过独立 hook 管理，做到断线重连、状态补拉和页面回收。

### 11.3 核心前端能力
- 大表单商品建档。
- 多图上传与上传进度。
- 资产状态可视化。
- 产物配置面板。
- PromptDraft 普通模式 / 高级模式切换。
- 预计扣费悬浮明细。
- 任务流式状态展示。
- 结果瀑布流、版本树和继续优化。
- Mask 编辑器。
- 管理后台复杂表格与配置页。

### 11.4 交互要求
- 所有扣费动作前必须有明确确认与费用提示。
- 所有失败任务必须展示可读失败原因，而不是只显示代码。
- 管理后台配置变更应提示“新任务生效、历史任务不回写”。
- 导出操作必须异步化，不阻塞主页面。

---

## 12. 数据库设计

### 12.1 通用约定
- 主键统一采用 `uuid`
- 时间字段使用 `timestamptz`
- 大部分可扩展字段采用 `jsonb`
- 关键查询字段建立普通索引或 GIN 索引
- 金额字段全部使用整数积分，不使用浮点

### 12.2 枚举建议
- `platform`：`amazon` / `douyin`
- `product_type`：`apparel` / `3c` / `home` / `beauty` / `other`
- `asset_type`：`original` / `cutout` / `mask` / `thumbnail` / `reference` / `output` / `export_zip`
- `recipe_scope`：`system` / `workspace` / `user`
- `job_status`：`queued` / `running` / `partial_succeeded` / `succeeded` / `failed` / `canceled`
- `job_item_status`：`queued` / `running` / `succeeded` / `failed` / `canceled`
- `generation_kind`：`image` / `video` / `text` / `template`
- `credit_ledger_type`：`recharge` / `hold` / `capture` / `release` / `refund` / `adjust` / `redeem`
- `provider_type`：`image` / `video` / `llm` / `matting`

### 12.3 核心表

#### 12.3.1 组织权限
**users**
- id uuid pk
- email text unique not null
- password_hash text not null
- is_system_admin bool not null default false
- status text not null default 'active'
- created_at / updated_at

**workspaces**
- id uuid pk
- name text not null
- owner_user_id uuid fk users(id)
- settings jsonb not null default '{}'
- created_at / updated_at

**memberships**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- user_id uuid fk users(id)
- role text not null
- created_at / updated_at
- unique(workspace_id, user_id)

**audit_logs**
- id uuid pk
- workspace_id uuid nullable
- user_id uuid nullable
- action text not null
- entity_type text not null
- entity_id uuid nullable
- payload jsonb not null default '{}'
- created_at timestamptz not null default now()

#### 12.3.2 商品与资产
**products**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- name text not null
- product_type text not null
- profile jsonb not null default '{}'
- notes text nullable
- platform_states jsonb not null default '{}'
- status text not null default 'draft'
- created_at / updated_at

**assets**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- product_id uuid fk products(id) nullable
- type text not null
- file_key text unique not null
- mime_type text not null
- width int nullable
- height int nullable
- sha256 text nullable
- meta jsonb not null default '{}'
- created_at / updated_at

#### 12.3.3 品牌、平台、配方、模板
**brand_profiles**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- name text not null
- version int not null
- is_active bool not null default false
- data jsonb not null default '{}'
- created_at / updated_at

**platform_profiles**
- id uuid pk
- platform text not null
- version int not null
- rules jsonb not null default '{}'
- defaults jsonb not null default '{}'
- created_at / updated_at

**recipes**
- id uuid pk
- scope text not null
- workspace_id uuid nullable
- owner_user_id uuid nullable
- platform text not null
- category text not null
- name text not null
- status text not null default 'active'
- latest_version int not null default 1
- created_at / updated_at

**recipe_versions**
- id uuid pk
- recipe_id uuid fk recipes(id)
- version int not null
- spec jsonb not null
- created_by uuid fk users(id)
- created_at / updated_at

**packs**
- id uuid pk
- scope text not null
- workspace_id uuid nullable
- owner_user_id uuid nullable
- platform text not null
- name text not null
- items jsonb not null
- created_at / updated_at

**poster_templates**
- id uuid pk
- scope text not null
- workspace_id uuid nullable
- platform text not null
- name text not null
- template_json jsonb not null
- preview_asset_id uuid nullable
- created_at / updated_at

#### 12.3.4 提示词、任务、结果
**prompt_drafts**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- product_id uuid fk products(id)
- platform text not null
- category text not null
- recipe_id uuid fk recipes(id)
- recipe_version int not null
- draft jsonb not null
- status text not null default 'draft'
- parent_id uuid nullable
- created_by uuid fk users(id)
- created_at / updated_at

**jobs**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- product_id uuid fk products(id)
- platform text not null
- status text not null default 'queued'
- credits_estimated int not null default 0
- credits_frozen int not null default 0
- credits_captured int not null default 0
- created_by uuid fk users(id)
- created_at / updated_at

**job_items**
- id uuid pk
- job_id uuid fk jobs(id)
- category text not null
- recipe_id uuid fk recipes(id)
- recipe_version int not null
- prompt_draft_id uuid nullable
- status text not null default 'queued'
- attempt int not null default 0
- max_attempts int not null default 2
- provider text nullable
- provider_model text nullable
- params jsonb not null default '{}'
- model_snapshot jsonb not null default '{}'
- pricing_snapshot jsonb not null default '{}'
- credits_estimated int not null default 0
- credits_captured int not null default 0
- error_code text nullable
- error_message text nullable
- created_at / updated_at

**generations**
- id uuid pk
- job_item_id uuid fk job_items(id)
- workspace_id uuid fk workspaces(id)
- product_id uuid fk products(id)
- category text not null
- kind text not null
- asset_id uuid nullable fk assets(id)
- text_content text nullable
- meta jsonb not null default '{}'
- parent_generation_id uuid nullable
- created_by uuid fk users(id)
- created_at / updated_at

#### 12.3.5 钱包、账本、充值卡
**credit_wallets**
- id uuid pk
- workspace_id uuid fk workspaces(id) unique
- balance int not null default 0
- frozen_balance int not null default 0
- updated_at timestamptz not null default now()

**credit_ledgers**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- user_id uuid fk users(id) nullable
- type text not null
- amount int not null
- related_entity_type text nullable
- related_entity_id uuid nullable
- note text nullable
- idempotency_key text nullable
- created_at timestamptz not null default now()

**recharge_card_batches**
- id uuid pk
- name text not null
- credits_amount int not null
- total_count int not null
- issued_count int not null default 0
- status text not null default 'active'
- expires_at timestamptz nullable
- created_by uuid fk users(id)
- created_at timestamptz not null default now()

**recharge_cards**
- id uuid pk
- batch_id uuid fk recharge_card_batches(id)
- card_code text unique not null
- credits_amount int not null
- status text not null default 'unused'
- expires_at timestamptz nullable
- issued_to_workspace_id uuid nullable
- created_at timestamptz not null default now()

**recharge_redemptions**
- id uuid pk
- recharge_card_id uuid fk recharge_cards(id)
- workspace_id uuid fk workspaces(id)
- redeemed_by uuid fk users(id)
- created_at timestamptz not null default now()

---

## 13. 配方系统、模型管理与路由策略

### 13.1 配方分类建议
- `main_image_enhance`
- `scene_image`
- `model_image_showcase`
- `model_image_inuse`
- `detail_image`
- `poster_selling`
- `poster_social`
- `size_chart`
- `core_params`
- `parts_annotation`
- `multi_angle`
- `long_detail_page`
- `copywriting_title`
- `copywriting_desc`
- `video_scene`

### 13.2 RecipeVersion.spec 建议结构
- `inputs`：输入要求
- `strategy`：执行策略
- `output`：输出规格
- `controls`：前端可调控制项
- `prompt`：提示词模板
- `provider_requirements`：能力需求与主备策略
- `pricing_tags`：定价匹配标签
- `limits`：超时与重试控制
- `compliance`：平台规则和阻断项

### 13.3 PromptDraft 规则
- 产品结构化字段只能进入事实槽位。
- 用户自由文本只能进入补充描述槽位。
- 平台规则与合规规则不能被用户输入覆盖。
- LLM 输出必须经过 JSON Schema 校验。

### 13.4 Provider 与模型管理
系统必须支持以下治理能力：
- 一个 Provider 下挂多个模型。
- 模型声明支持的能力与默认参数。
- 多个模型组成模型组，支持权重与主备优先级。
- 路由策略按工作区、平台、分类、配方、商品类型等维度匹配。
- 每个 JobItem 要记录最终命中的 Provider、模型和执行参数快照。

### 13.5 路由选择原则
1. 工作区级策略优先于系统级策略。
2. `recipe_id` 优先级高于 `category`，`category` 高于 `platform`。
3. 先选主模型组，再选组内模型。
4. 遇到限流、超时、5xx 等可回退错误时切到备模型组。
5. 若全部失败，标记任务失败并写出建议。

### 13.6 降级交付策略
- 背景生成失败：使用背景素材库检索并执行后期合成。
- 局部重绘失败：保底提供主体融合、阴影和边缘羽化方案。
- 视频生成失败：降级为关键帧动效视频。
- 复杂 try-on 不支持时：降级为展示型模特图并明确提示。

---

## 14. 积分、定价、充值卡与账本体系

### 14.1 计费原则
- 所有积分均为整数。
- 所有任务开始前展示预计扣费。
- 创建任务后先冻结积分，再按 JobItem 实际成功情况逐项结算。
- 失败项必须释放冻结额度。
- 退款、补偿、手工调账都必须进入账本。

### 14.2 价格配置目标
后台必须能按以下维度控制价格：
- 平台
- 产物类别
- 配方
- 模型或模型组
- 分辨率档位
- 输出数量
- 扩展标记，例如 `inpaint`、`upscale`、`video`

### 14.3 价格规则结构
**price_plans**
- id
- scope
- workspace_id
- name
- version
- status
- rules_meta

**price_rules**
- id
- plan_id
- priority
- match
- formula
- enabled

### 14.4 价格公式
推荐统一使用结构化公式，不允许直接执行字符串表达式：

```json
{
  "base": 6,
  "per_output": 2,
  "size_add": {
    "s": 0,
    "m": 2,
    "l": 6,
    "xl": 10
  },
  "flag_add": {
    "inpaint": 2,
    "upscale": 3,
    "template_render": 2,
    "video": 8
  },
  "model_coef": {
    "default": 1.0,
    "providerB:modelY": 1.3
  },
  "rounding": "ceil_int"
}
```

统一计算口径：

`credits = ceil_int((base + per_output * count + size_add + sum(flag_add)) * model_coef)`

### 14.5 充值卡设计
当前不做支付，但必须支持完整充值卡能力：
- 系统管理员创建充值卡批次。
- 每个批次生成唯一卡密。
- 卡密支持失效时间和状态流转。
- 工作区管理员在前台兑换卡密。
- 兑换成功后立即入钱包并写账本与兑换记录。
- 已兑换、已作废、已过期卡密不可重复使用。

### 14.6 钱包与账本规则
- `recharge`：充值卡充值或后台加积分。
- `hold`：创建任务冻结。
- `capture`：任务成功结算。
- `release`：失败释放。
- `refund`：人工退款或补偿。
- `adjust`：后台调账。
- `redeem`：充值卡兑换事件。

### 14.7 幂等要求
- `capture` 以 `job_item_id` 为幂等主键。
- 充值卡兑换以 `recharge_card_id` 为幂等主键。
- 后台调账必须有唯一流水标识，防止重复提交。

---

## 15. 异步任务、SSE 与生成执行体系

### 15.1 队列划分
- `q_matting`
- `q_image_gen`
- `q_render`
- `q_video_gen`
- `q_export`
- `q_llm`

### 15.2 必要任务
- `process_asset(asset_id)`
- `run_job_item(job_item_id)`
- `render_template(job_item_id)`
- `export_zip(export_id)`
- `llm_improve_prompt(prompt_draft_id)`
- `llm_generate_copywriting(product_id, platform, languages)`

### 15.3 任务状态机
- Job：`queued -> running -> partial_succeeded / succeeded / failed / canceled`
- JobItem：`queued -> running -> succeeded / failed / canceled`

### 15.4 SSE 推送规则
- Worker 更新状态后发布 Redis 事件。
- API 层订阅并转发到 `/api/jobs/{id}/events`。
- 前端收到事件后更新任务列表、单项状态和结果流。
- 若 SSE 断开，前端必须自动补拉最近状态。

### 15.5 幂等与重试
- 读取到任务已完成或已取消时，不重复执行。
- 只对可重试错误重试。
- 最大重试次数由配方或任务配置决定。
- 多次失败后保留完整错误信息供运营复盘。

---

## 16. 模板渲染、资产处理与 COS 方案

### 16.1 模板渲染
所有带文本的可交付图片必须走后端模板渲染，模板 JSON 建议包含：
- 画布大小
- 背景图层
- 商品图层
- 文本图层
- 卖点标签图层
- 图标与装饰图层

模板引擎需支持：
- 自动换行
- 最大行数
- 自动缩放字体
- 阴影、描边、透明度
- 多 section 拼接成长图

### 16.2 资产预处理
- 生成缩略图
- 计算 SHA256
- 识别尺寸和 MIME
- 调用第三方或内部能力生成 cutout 和 mask
- 为继续优化场景保存可复用中间结果

### 16.3 COS 上传方案
推荐采用 STS 前端直传：
- 前端先取上传凭证。
- 上传完成后调用资产入库接口。
- 后端异步触发预处理。

### 16.4 COS Key 规范
`{env}/{workspace_id}/{product_id}/{asset_type}/{uuid}.{ext}`

### 16.5 下载与权限
- 所有对象默认私有。
- 下载通过后端签发短期有效 URL。
- 导出包与结果图的访问都必须经过权限校验。

---

## 17. 管理后台与运营使用方案

### 17.1 Provider 管理
- 维护第三方供应商 Key
- 启停模型
- 查看错误率和健康状态
- 管理参数范围和默认值

### 17.2 路由与价格管理
- 维护模型组
- 管理工作区定向路由
- 发布价格方案
- 模拟价格估算结果

### 17.3 充值卡运营
- 创建充值卡批次
- 批量生成卡密
- 设定积分面额和过期时间
- 作废卡密
- 查询卡密使用状态
- 追溯某个工作区的兑换历史

### 17.4 运营监控
- 查看全站任务趋势
- 查看失败类型排行
- 查看高频扣费工作区
- 查看队列积压
- 查看可疑频繁重试和异常刷卡行为

### 17.5 审计要求
以下动作必须审计：
- 模型启停
- 路由变更
- 价格方案发布
- 配方和模板发布
- 充值卡生成、作废、兑换
- 后台调账
- 导出和批量下载

---

## 18. 本地开发、部署与运维方案

### 18.1 本地开发环境
- 操作系统：Windows + pwsh7
- Python 包管理：`uv`
- Node：前端标准 Node 环境
- 数据库：PostgreSQL，优先使用项目指定的开发库
- Redis：本地或局域网 Redis

本项目本地开发默认与生产保持一致，不使用 SQLite 作为主开发数据库。

### 18.2 本地开发服务
- `frontend`：React 开发服务器
- `backend`：FastAPI 应用
- `worker-default`：Celery Worker
- `worker-video`：视频 Worker
- `redis`
- `postgres`

### 18.3 推荐环境变量
```bash
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
REDIS_URL=redis://:pass@host:6379/0
JWT_SECRET=replace_me
COS_BUCKET=replace_me
COS_REGION=replace_me
COS_STS_SECRET_ID=replace_me
COS_STS_SECRET_KEY=replace_me
APP_ENV=dev
API_BASE_URL=https://your-domain/api
```

### 18.4 Docker Compose 落地方案
生产环境采用单机或单虚拟机 Docker Compose：
- `nginx`
- `frontend`
- `api`
- `worker-default`
- `worker-video`
- `redis`
- `postgres`

关键要求：
- `nginx` 负责 HTTPS、静态资源和 API 转发。
- `api` 与 worker 共享同一镜像或同一代码版本。
- `redis` 与 `postgres` 使用持久化卷。
- `frontend` 产物建议构建后交由 Nginx 托管。

### 18.5 部署流程
1. 拉取代码。
2. 更新环境变量。
3. 构建镜像。
4. 执行数据库迁移。
5. 启动或滚动重启 Compose 服务。
6. 校验 API、前端、SSE、Worker 和导出链路。

### 18.6 回滚策略
- 镜像按版本号保留。
- 数据库迁移必须前向兼容或提供回滚策略。
- 如新版本任务异常，优先回滚 `frontend` 与 `api/worker` 镜像。
- 涉及价格和路由变更时，后台配置本身也要有版本记录与可回滚能力。

### 18.7 运维 SOP
- 查看任务失败：先看 `job_items.error_code` 与 `error_message`，再查 Worker 日志。
- 查看队列积压：检查 Redis、Worker 并发和第三方模型限流。
- 查看扣费异常：比对 `jobs`、`job_items` 与 `credit_ledgers`。
- 查看充值卡异常：检查 `recharge_cards.status` 和 `recharge_redemptions`。
- 数据备份：定时备份 PostgreSQL；导出包与结果图依赖 COS 生命周期管理。

---

## 19. 安全、合规、风控与观测

### 19.1 安全
- 工作区资源必须强隔离。
- COS 临时凭证仅允许特定前缀上传。
- 下载链接短时有效。
- 敏感配置放环境变量，不写死在仓库。
- 后台操作采用严格 RBAC。

### 19.2 合规
- 平台规则支持提示级、警告级、阻断级三种策略。
- Amazon 主图等强规则可在配方和模板层内置限制。
- 禁宣词和高风险词应支持品牌档案和平台规则双层校验。

### 19.3 风控
- 用户和工作区维度限流。
- Provider 和模型维度限流。
- 高频重试、异常导出、异常刷卡、异常调用量必须可识别。

### 19.4 观测指标
- Provider 成功率和延迟
- 任务成功率和失败原因分布
- 队列长度与等待时长
- 钱包余额与冻结差异
- 充值卡生成、兑换、失效率
- 导出成功率与文件大小分布

### 19.5 日志规范
- 结构化 JSON 日志
- 包含 `request_id`、`user_id`、`workspace_id`、`job_id`
- 区分业务日志、错误日志、审计日志、第三方调用日志

---

## 20. 测试策略与验收标准

### 20.1 测试层次
- 单元测试：价格公式、账本幂等、路由匹配、权限校验。
- 集成测试：任务创建、冻结、执行、结算、释放全链路。
- 契约测试：前后端接口结构、错误码、分页和 SSE 事件格式。
- E2E 测试：商品建档、上传、生成、优化、导出、充值卡兑换。
- 压力测试：多工作区并发生产和后台管理配置并发读取。

### 20.2 核心验收场景
- 用户能创建工作区并邀请成员。
- 用户能创建商品并上传图片。
- 系统能完成抠图和资产预处理。
- 用户能查看预计扣费并成功提交任务。
- 图片、海报、详情长图、文案、视频均能生成并落库。
- 某个任务部分失败时，状态和扣费处理正确。
- 用户能继续优化某个结果并形成版本树。
- 用户能批量导出并拿到签名下载链接。
- 工作区管理员能成功兑换充值卡，积分到账正确。
- 系统管理员能调整价格、模型和路由，并作用于新任务。

### 20.3 上线验收标准
上线前必须确认：
- 登录、权限、工作区隔离无明显缺陷。
- 账本无重复扣费或释放异常。
- 充值卡无重复兑换漏洞。
- SSE 在正常网络抖动下可恢复。
- Docker Compose 能一键起服务并完成迁移。
- 日志和监控能支撑问题排查。

---

## 21. 完整建设顺序与模块依赖

本项目不采用 MVP 思路，但工程实现仍需遵守依赖顺序。推荐顺序如下：

1. 基础设施
   - 项目骨架、配置管理、数据库连接、Redis、日志、错误处理、统一响应。
2. 身份与组织
   - 用户、登录、工作区、成员、RBAC、审计。
3. 商品与资产
   - 商品建档、品牌档案、上传、COS 记录、资产预处理。
4. 配方与模板
   - 配方中心、产物包、模板中心、平台方案、PromptDraft 编译。
5. 模型治理
   - Provider、模型、模型组、路由策略、限流机制。
6. 积分与充值卡
   - 钱包、账本、价格规则、价格估算、充值卡、后台调账。
7. 任务与结果
   - Job、JobItem、Generation、SSE、失败重试。
8. 图像与文案生产链路
   - 主图、场景图、海报、详情图、文案。
9. 视频生产链路
   - 正式视频与关键帧降级链路。
10. 继续优化与版本树
   - 局部重绘、风格微调、风格锚点。
11. 导出与交付
   - 批量导出、压缩包、下载权限。
12. 运营后台
   - 审计、监控、异常处理、批量治理。
13. 部署与上线治理
   - Docker Compose、备份、日志、告警、上线清单。

---

## 22. 风险边界与后续演进方向

### 22.1 当前风险边界
1. 单图生成多角度结果属于“表现近似”，不承诺真实物理结构复原。
2. 对内部结构和不可见零部件，不做无依据的真实生成。
3. 使用型模特图和 try-on 场景受外部模型能力限制，必须保留降级路径。
4. 视频生成受第三方模型波动影响明显，必须有失败补偿与降级方案。
5. 图片、模板和视频能力越多，价格规则和路由治理复杂度越高，后台必须先天具备版本化能力。

### 22.2 后续演进方向
以下能力可作为后续扩展，但不属于当前必须建设项：
- 在线支付和订单中心
- 对外开放 API
- 多语言界面
- 云原生部署与自动弹性扩缩容
- 数据分析看板和产出效果评估体系

---

## 附：关键决策一览

- 项目名称：尚图工坊
- 文档性质：项目唯一总纲
- 产品形态：多租户 SaaS
- 前端：React + Ant Design
- 后端：FastAPI + SQLAlchemy + PostgreSQL
- 异步：Celery + Redis
- 存储：腾讯云 COS
- 计费：整数积分
- 充值：管理员生成充值卡 + 后台调账
- 支付：当前不做在线支付
- 部署：Linux Docker Compose
- 能力范围：图片、海报、详情长图、文案、视频全部纳入正式范围
