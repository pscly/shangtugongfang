# 电商素材工厂｜完整开发设计文档（FastAPI + SQLAlchemy + PostgreSQL + Celery + COS）
**版本**：v1.1
**日期**：2026-03-25
**站点语言**：中文 UI（生成内容可选：中文 / 英文 / 中英）
**目标平台**：Amazon、抖音小店
**计费确认**：积分必须是整数；任务开始前展示“预计扣费”；扣费采用冻结→结算→释放/退款。

---

## 目录
1. 总览与目标
2. 角色、权限与审计
3. 核心概念与业务对象
4. 全链路业务流程（端到端）
5. 系统架构与技术选型
6. 数据库设计（表、枚举、索引、约束）
7. 配方系统（Recipe / Pack / PromptDraft）规范
8. Provider / 模型管理与路由（主备、降级、限流）
9. 定价与积分计费引擎（后台可配置、版本化、快照）
10. 异步任务体系（Celery 队列、幂等、重试）
11. 模板渲染系统（海报/尺寸/参数/详情长图，后端渲染）
12. 资产与 COS（上传、签名、处理、抠图）
13. API 设计（用户端 + 管理端，含主要 Schema）
14. 前端设计（React + Ant Design：页面、组件、数据流、SSE）
15. 管理后台（功能清单与页面结构）
16. 安全、合规、风控与限流
17. 观测与运维（日志、指标、告警）
18. 部署与环境（腾讯云建议架构）
19. 测试策略（单测/集成/契约/E2E）
20. 局限性与风险边界（必须写入产品说明）
21. 开发任务拆分与依赖顺序（不改变最终功能边界）

---

## 1. 总览与目标

### 1.1 产品目标
为电商卖家提供“同款一致性”的素材生产工作台：
- **输入**：产品结构化信息 + 产品白底图/多图 + 平台（Amazon/抖音） +（可选）品牌档案/全局风格
- **输出**：图像、海报、详情长图、文案、视频，并支持迭代优化、版本追溯、批量导出与积分计费。

### 1.2 关键设计原则（研发共识）
1) **同款一致性优先**：默认锁定产品主体（来自用户真实图片的 cutout + mask），主要生成背景/光影/道具与融合。
2) **模板渲染优先**：凡涉及文字（卖点海报/社媒海报/尺寸/参数/详情长图）必须后端模板渲染，不让扩散模型“画字”。
3) **计费可解释可追溯**：每个 JobItem 必须写入定价快照与模型快照；积分流水必须账本化。
4) **平台方案切换**：Amazon/抖音不是皮肤，是规则、默认配方、推荐产物组合与风格差异的集合。
5) **可降级交付**：三方 API 不可用时仍尽量交付（背景用素材库、视频用关键帧动效等）。

---

## 2. 角色、权限与审计

### 2.1 角色
- **系统超级管理员（SystemAdmin）**：全站 Provider/模型/路由/定价/全局配方、审计。
- **工作区 Owner**：成员管理、充值、工作区配方模板发布。
- **工作区 Admin**：协助管理。
- **Member**：生产与导出。
- **Viewer（可选）**：只读/下载（可配置）。

### 2.2 权限要点
- 配方/模板：系统内置只读；工作区由 Owner/Admin 发布；Member 可复制为私有并改。
- 积分：Owner/Admin 可看工作区全流水；Member 默认只看自己相关流水（可配置）。
- **审计**：充值/调价/配方发布/导出/批量下载/管理员调整积分/变更 Provider Key 必须写 audit_logs。

---

## 3. 核心概念与业务对象（术语统一）

- **Workspace**：店铺/团队隔离边界（成员、资产、积分归属）。
- **PlatformProfile**：Amazon / Douyin 平台方案（规则+默认输出+推荐 Pack/Recipe）。
- **BrandProfile**：品牌档案（全局风格、人群、禁宣、关键词、配色、平台偏好）。
- **Product**：产品档案（结构化事实字段 + 自由说明 + 资产集合）。
- **Asset**：文件资产（原图、cutout、mask、输出、模板预览…存 COS）。
- **Recipe / RecipeVersion**：可执行配方与版本（输入要求、策略、参数、提示词模板、降级、定价标签）。
- **Pack**：产物包（用户勾选项集合，一键生成多类）。
- **PromptDraft**：提示词草稿（可编辑/可 AI 优化/可版本链）。
- **Job / JobItem**：一次批量任务与最小执行单元（1 个 JobItem = 1 个输出文件）。
- **Generation**：生成结果（关联输出 Asset 或文本内容），支持版本树迭代。
- **Provider / ProviderModel / ModelGroup / RoutingPolicy**：三方服务与模型管理、模型组、路由策略（主备、权重、回退）。
- **PricePlan / PriceRule**：定价方案与规则（后台可配置、版本化）。
- **CreditWallet / CreditLedger**：积分余额与账本流水（整数）。

---

## 4. 全链路业务流程（端到端）

### 4.1 产品创建与资产处理
1) 新建产品（结构化表单：类目/材质/尺寸/卖点/禁宣等）。
2) 上传图片（至少 1 张白底；建议支持多图）。
3) 触发资产处理（Celery）：缩略图、三方抠图 → 得到 cutout PNG + mask PNG。
4) 资产状态回写、前端显示“可生成”。

### 4.2 平台切换与产物选择
1) 进入产品工作台，切换平台 Tab（Amazon/抖音）。
2) 选择 Pack（推荐）或按分类勾选（可自定义并保存）。
3) 为每个分类选择 Recipe（默认由平台方案提供，可改）。

### 4.3 提示词草稿与确认
1) 点击“生成草稿”：系统按「产品事实 + 品牌档案 + 平台规则 + 配方模板 + 控制项」编译 PromptDraft。
2) 用户可：
   - 普通模式：改“控制项”（场景主题/氛围/道具密度/光线等）
   - 高级模式：查看/编辑完整提示词，或“AI 优化提示词”（生成新版本草稿）

### 4.4 生成执行与计费
1) 点击“开始生成”前：前端展示**预计扣费（整数积分）**与扣费明细（简化版 breakdown）。
2) 创建 Job：后端计算预估成本 → 校验余额 → 冻结积分（hold） → 创建 Job/JobItem 入队。
3) Worker 执行：更新状态、推送 SSE 事件、成功后结算（capture），失败释放（release）。
4) 前端按分类瀑布流实时展示结果。

### 4.5 迭代优化（图下继续优化）
- 对某张图：输入优化词 → 选择模式
  - **只改背景（默认）**：inpaint 仅 mask 外区域
  - **局部重绘**：前端涂抹 mask（Konva/Fabric）
  - **轻度风格微调**：img2img 低强度（仍强调锁产品）
- 形成 Generation 版本树（parent_generation_id）。

### 4.6 导出交付
- 单张下载、批量 zip 导出（Celery 生成 zip 上传 COS），海报/详情长图支持字段编辑后导出。

---

## 5. 系统架构与技术选型

### 5.1 技术栈
- 后端：FastAPI、SQLAlchemy 2.x、PostgreSQL（psycopg3）、Alembic、Celery、Redis
- 存储：腾讯云 COS（私有桶 + 签名下载；STS 前端直传）
- 前端：React + Ant Design（推荐；若 Vue3 亦可同构）
- 实时：SSE（FastAPI StreamingResponse + Redis PubSub）

### 5.2 服务分层
- `api`：鉴权、业务 API、SSE、管理后台 API
- `worker`：Celery 执行器（生成/抠图/渲染/导出/LLM）
- `redis`：Celery broker + PubSub
- `postgres`：主数据库
- `cos`：对象存储

---

## 6. 数据库设计（表、枚举、索引、约束）

### 6.1 通用字段规范
- 主键：`uuid`（应用层生成，避免分库迁移问题）
- 时间：`timestamptz`
- 软删：关键表加 `deleted_at`（可选）
- JSON：`jsonb`，并对可检索字段建立 GIN 索引
- 所有写操作带 `updated_at`，并用 `version int`（乐观锁可选）

### 6.2 枚举（建议以 text + 校验实现，便于扩展）
- `platform`：`amazon` / `douyin`
- `product_type`：`apparel` / `3c` / `home` / `beauty` / `other`
- `asset_type`：`original` / `cutout` / `mask` / `thumbnail` / `detail_crop` / `reference` / `output`
- `recipe_scope`：`system` / `workspace` / `user`
- `job_status`：`queued` / `running` / `partial_succeeded` / `succeeded` / `failed` / `canceled`
- `job_item_status`：`queued` / `running` / `succeeded` / `failed` / `canceled`
- `generation_kind`：`image` / `video` / `text` / `template`
- `credit_ledger_type`：`recharge` / `hold` / `capture` / `release` / `refund` / `adjust`
- `provider_type`：`image` / `video` / `llm` / `matting`
- `capability`：`t2i` / `inpaint` / `img2img` / `upscale` / `video` / `text` / `matting`

### 6.3 核心表（摘要）
> 下列为“必须表”；字段精确到可直接建表。可用 Alembic 生成迁移。

#### 6.3.1 组织权限
**users**
- id uuid pk
- email text unique not null
- password_hash text not null
- is_system_admin bool not null default false
- status text not null default 'active'
- created_at/updated_at

**workspaces**
- id uuid pk
- name text not null
- owner_user_id uuid fk users(id)
- settings jsonb not null default '{}'
- created_at/updated_at

**memberships**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- user_id uuid fk users(id)
- role text not null
- created_at/updated_at
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
- index(workspace_id, created_at)

#### 6.3.2 产品与资产
**products**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- name text not null
- product_type text not null
- profile jsonb not null default '{}'   *(结构化事实字段)*
- notes text nullable
- platform_states jsonb not null default '{}' *(Amazon/抖音各自最近选择/风格锚点等)*
- status text not null default 'draft'
- created_at/updated_at
- index(workspace_id, updated_at)
- gin(profile)

**assets**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- product_id uuid fk products(id) nullable
- type text not null
- file_key text unique not null  *(COS key)*
- mime_type text not null
- width int nullable
- height int nullable
- sha256 text nullable
- meta jsonb not null default '{}'
- created_at/updated_at
- index(product_id, type)

#### 6.3.3 品牌/平台方案
**brand_profiles**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- name text not null
- version int not null
- is_active bool not null default false
- data jsonb not null default '{}'
- created_at/updated_at
- index(workspace_id, is_active)

**platform_profiles**（系统内置）
- id uuid pk
- platform text not null
- version int not null
- rules jsonb not null default '{}'
- defaults jsonb not null default '{}'
- created_at/updated_at
- unique(platform, version)

#### 6.3.4 配方/产物包/模板
**recipes**
- id uuid pk
- scope text not null
- workspace_id uuid nullable
- owner_user_id uuid nullable
- platform text not null  *(amazon/douyin/universal 可扩展)*
- category text not null
- name text not null
- status text not null default 'active'
- latest_version int not null default 1
- created_at/updated_at
- index(platform, category, status)

**recipe_versions**
- id uuid pk
- recipe_id uuid fk recipes(id)
- version int not null
- spec jsonb not null
- created_by uuid fk users(id)
- created_at/updated_at
- unique(recipe_id, version)

**packs**
- id uuid pk
- scope text not null
- workspace_id uuid nullable
- owner_user_id uuid nullable
- platform text not null
- name text not null
- items jsonb not null  *([{category, recipe_id, recipe_version, count_override, ...}])*
- created_at/updated_at

**poster_templates**
- id uuid pk
- scope text not null
- workspace_id uuid nullable
- platform text not null
- name text not null
- template_json jsonb not null
- preview_asset_id uuid nullable fk assets(id)
- created_at/updated_at

#### 6.3.5 PromptDraft / Job / Generation
**prompt_drafts**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- product_id uuid fk products(id)
- platform text not null
- category text not null
- recipe_id uuid fk recipes(id)
- recipe_version int not null
- draft jsonb not null  *(控制项 + 编译结果 + negative 等)*
- status text not null default 'draft'  *(draft/confirmed)*
- parent_id uuid nullable fk prompt_drafts(id)
- created_by uuid fk users(id)
- created_at/updated_at
- index(product_id, platform, category, created_at)

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
- created_at/updated_at
- index(workspace_id, created_at)

**job_items**
- id uuid pk
- job_id uuid fk jobs(id)
- category text not null
- recipe_id uuid fk recipes(id)
- recipe_version int not null
- prompt_draft_id uuid nullable fk prompt_drafts(id)
- status text not null default 'queued'
- attempt int not null default 0
- max_attempts int not null default 2
- provider text nullable
- provider_model text nullable
- params jsonb not null default '{}'          *(最终执行参数快照)*
- model_snapshot jsonb not null default '{}'  *(provider/model/params 快照)*
- pricing_snapshot jsonb not null default '{}'*(plan/rule/breakdown/整数积分快照)*
- credits_estimated int not null default 0
- credits_captured int not null default 0
- error_code text nullable
- error_message text nullable
- created_at/updated_at
- index(job_id)
- index(status)
- index(provider, provider_model, status)

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
- parent_generation_id uuid nullable fk generations(id)
- created_by uuid fk users(id)
- created_at/updated_at
- index(product_id, category, created_at)
- index(parent_generation_id)

#### 6.3.6 积分账本
**credit_wallets**
- id uuid pk
- workspace_id uuid fk workspaces(id) unique
- balance int not null default 0

**credit_ledgers**
- id uuid pk
- workspace_id uuid fk workspaces(id)
- user_id uuid fk users(id)
- type text not null
- amount int not null          *(整数，正负号表达加减)*
- related_entity_type text nullable
- related_entity_id uuid nullable
- note text nullable
- created_at timestamptz not null default now()
- index(workspace_id, created_at)
- index(related_entity_id)

---

## 7. 配方系统规范（Recipe / Pack / PromptDraft）

### 7.1 配方分类建议（category 枚举建议）
- `main_image_enhance`（主图修复/增强）
- `scene_image`（场景图）
- `model_image_showcase`（展示型模特图）
- `model_image_inuse`（使用型模特图：手持/佩戴/上身，可能降级）
- `detail_image`（细节图）
- `poster_selling`（卖点海报）
- `poster_social`（社媒海报）
- `size_chart`（尺寸图）
- `core_params`（核心参数图）
- `parts_annotation`（零部件图）
- `multi_angle`（多角度展示）
- `long_detail_page`（详情长图）
- `copywriting_title` / `copywriting_desc`
- `video_scene`（场景视频：校园/海边/自定义）

### 7.2 RecipeVersion.spec（建议 JSON Schema 约定）
> 这是研发与运营共同遵守的“配方契约”，后台编辑也按该结构存储。

**顶层字段**
- `inputs`：输入要求
- `strategy`：流水线策略（锁产品/背景生成/合成/inpaint/upscale/模板渲染等）
- `output`：输出规格（type/format/ratio/size/count）
- `controls`：前端可调控制项（enum/int/float/boolean/text）
- `prompt`：提示词模板（可分块；含 negative；可指定 prompt 语言）
- `provider_requirements`：能力需求 + 主备 provider/model 策略
- `pricing_tags`：定价标签（用于 price_rule 匹配，如 “inpaint”、“upscale”、“video_5s”）
- `limits`：超时/最大重试/安全限制
- `compliance`：平台合规提示/阻断规则（可选）

### 7.3 PromptDraft.draft 建议结构
```json
{
  "controls": { "scene_theme": "校园", "mood": "清爽", "props_density": 1 },
  "compiled": {
    "prompt_language": "en",
    "positive": "...",
    "negative": "..."
  },
  "policy": {
    "lock_product": true,
    "inpaint_outside_mask_only": true
  }
}
```

### 7.4 防“提示词注入”规则（强制）
- 产品结构化事实字段只能进入事实槽位；自由 notes 只能进入风格补充槽位；不得覆盖合规/规则槽位。
- Prompt 编译采用“拼装块”而非直接拼接用户整段文本。
- LLM 输出必须通过 JSON Schema 校验，不合格重试/拒绝。

---

## 8. Provider / 模型管理与路由（主备、降级、限流）

### 8.1 数据模型（新增表：模型与路由）
**providers**
- id, name, type(image/video/llm/matting), status
- auth_config(jsonb 加密)、rate_limit(jsonb)、health_meta(jsonb)

**provider_models**
- id, provider_id, model_code, display_name
- capabilities(jsonb array)
- default_params(jsonb)、param_schema(jsonb)
- max_output(jsonb)、status

**model_groups**
- id, type(image/video/llm/matting), name, strategy(jsonb)

**model_group_items**
- id, group_id, provider_model_id, weight, enabled, fallback_priority

**routing_policies**
- id, scope(system/workspace), workspace_id
- platform, category, recipe_id(optional), product_type(optional)
- model_group_id(primary), fallback_group_id(optional)
- priority, enabled

### 8.2 路由选择算法（后端固定实现）
1) 收集候选 routing_policies（workspace 优先于 system）。
2) 规则匹配优先级：`recipe_id > category > platform > universal`；再按 `priority` 降序。
3) 选择 primary group → 按 weight 随机/轮询选 model。
4) 若调用失败且属于可回退错误（限流/超时/5xx）→ 切 fallback group。
5) 仍失败 → job_item failed，并写 error_code/建议。

### 8.3 降级交付策略（必须）
- 背景生成失败：使用“背景素材库”检索（按场景主题/风格标签）→ 合成
- inpaint 失败：仅做阴影+边缘羽化融合
- 视频失败：关键帧动效视频（生成 3~5 张关键帧 + 转场 + 轻微位移缩放）

> 背景素材库可做成 `assets` 的特殊归属（product_id 为空、meta.tags 包含场景标签），由管理员维护。

### 8.4 限流（必须做三层）
- provider/model 维度：并发与 QPS
- workspace 维度：并发 job_item 上限
- user 维度：并发上限/每分钟创建 job 限制
实现建议：Redis 信号量（Lua 原子 acquire/release）。

---

## 9. 定价与积分计费引擎（后台可配置、版本化、快照）
你已确认：**积分为整数**；**任务开始前展示预计扣费**。

### 9.1 价格配置目标
- 你在后台可随时调整：不同平台/不同产物/不同模型/不同分辨率/不同附加操作的扣费。
- 调价必须版本化：**新任务用新版本；历史任务保留快照**。

### 9.2 表结构（新增）
**price_plans**
- id, scope(system/workspace), workspace_id
- name, version(int), status(active/archived)
- rules_meta(jsonb)

**price_rules**
- id, plan_id, priority
- match(jsonb)
- formula(jsonb)  *(组件化公式，不允许 eval 字符串)*
- enabled

> JobItem 必须写入：`pricing_snapshot`（plan_id, rule_id, breakdown, credits_estimated）。

### 9.3 match 字段枚举（统一约定，后台表单也按此）
`match` 可包含（均可选）：
- platform: amazon/douyin
- category: scene_image/poster_selling/...
- recipe_id
- provider_id / provider_model_id（可精确到某模型）
- output_type: image/video/template/text
- output_size_tier: `s(<=1024)` / `m(<=2048)` / `l(<=4096)` / `xl(>4096)`
- flags（数组）：如 `["inpaint","upscale","hd","video","template_render"]`
- duration_tier（视频）：`<=5s`, `<=10s`, `<=15s`, `>15s`
- product_type：apparel/3c/home/beauty/other
- workspace_id（仅 system plan 需要对特定客户定价时用；一般建议用 workspace scope plan）

### 9.4 formula 结构（整数积分）
示例（图像）：
```json
{
  "base": 6,
  "per_output": 2,
  "size_add": { "s": 0, "m": 2, "l": 6, "xl": 10 },
  "flag_add": { "inpaint": 2, "upscale": 3, "template_render": 2, "hd": 2 },
  "model_coef": { "default": 1.0, "providerB:modelY": 1.3 },
  "rounding": "ceil_int"
}
```

**计算口径（后端实现固定）**
`credits = ceil_int( (base + per_output*count + size_add + Σflag_add) * model_coef )`
保证输出为整数。

### 9.5 预计扣费展示（创建 Job 前）
- 前端调用：`POST /api/pricing/estimate`（建议新增）
  - 入参：platform、items（category/recipe_version/output size/count/flags/model(optional)）
  - 返回：总预计积分 + 每个 item 的 breakdown（可简化展示）
- 创建 Job 时后端再次估算并冻结（防止前端篡改）。

### 9.6 冻结→结算→释放（账本规则）
- hold：创建 job 时冻结总额（整数）
- capture：每个 job_item 成功后结算其 credits（整数）
- release：job_item 失败/取消释放其冻结额度
- job 完成时释放剩余冻结（若预估 > 实际）

**幂等要求**
- capture 以 `job_item_id` 为幂等键；同一 item 不得重复 capture。

---

## 10. 异步任务体系（Celery）

### 10.1 Broker/Backend
- Redis 作为 broker + backend（或 backend 也可用 DB，但 Redis 更简洁）

### 10.2 队列划分（建议）
- `q_matting`：抠图/资产处理
- `q_image_gen`：图像生成/融合/超分
- `q_render`：模板渲染（海报/详情长图）
- `q_video_gen`：视频生成/动效降级
- `q_export`：批量导出 zip
- `q_llm`：提示词优化/文案生成

### 10.3 任务列表（建议必须实现）
- `process_asset(asset_id)`：缩略图、sha256、抠图、mask、cutout 生成
- `run_job_item(job_item_id)`：执行图像/视频/模板/文案的流水线
- `render_template(job_item_id)`：模板渲染输出 asset
- `export_zip(export_id)`：打包 zip → COS
- `llm_improve_prompt(prompt_draft_id)`
- `llm_generate_copywriting(product_id, platform, languages)`

### 10.4 幂等与重试
- 每个 task 开始时读取 job_item，若 status 已为 succeeded/failed/canceled，直接返回。
- provider 调用失败：仅对“可重试错误”重试（超时/5xx/限流）；参数错误不重试。
- attempt 递增并写库；超过 max_attempts 失败。

### 10.5 状态推送（SSE）
- worker 每次写 job_item 状态后 publish Redis：`job:{job_id}`
- API SSE 订阅该 channel 并转发给前端。

---

## 11. 模板渲染系统（后端渲染）

### 11.1 模板 JSON 规范（poster_templates.template_json）
建议结构：
```json
{
  "canvas": { "width": 1080, "height": 1920, "background": "#FFFFFF" },
  "layers": [
    { "type": "image", "id": "bg", "source": "{{asset.bg}}", "fit": "cover" },
    { "type": "image", "id": "product", "source": "{{asset.product_cutout}}", "x": 120, "y": 420, "w": 840, "h": 840 },
    { "type": "text", "id": "title", "text": "{{copy.title}}", "x": 80, "y": 120, "w": 920, "font": "SourceHanSans", "size": 56, "color": "#111", "max_lines": 2, "auto_shrink": true }
  ]
}
```

### 11.2 后端渲染实现建议
- Pillow + 自研排版（自动换行/缩放/描边/阴影）
- 字体：内置思源黑体/思源宋体（容器内挂载）
- 输出：PNG/JPG（PNG 优先，利于透明与边缘）

### 11.3 详情长图布局
- section 化：每个 section 用模板渲染（标题/卖点/细节/参数/尺寸/场景）
- 渲染后按高度拼接成单张长图
- 超长图建议分片渲染再拼接，防止内存峰值过高。

---

## 12. 资产与 COS

### 12.1 上传方案（推荐：STS 前端直传）
- `POST /api/uploads/cos/credentials`：返回临时凭证、允许前缀、过期时间
- 前端用 COS SDK 上传 → 再 `POST /api/assets/record` 入库
- 触发 `process_asset` 生成缩略/抠图

### 12.2 COS Key 规范（建议）
`{env}/{workspace_id}/{product_id}/{asset_type}/{uuid}.{ext}`
便于按 workspace 清理与审计。

### 12.3 下载（私有桶）
- `GET /api/assets/{id}/download-url`：后端签名 URL（短有效期）
- 前端通过该 URL 下载或展示。

---

## 13. API 设计（用户端 + 管理端）

### 13.1 统一约定
- Base：`/api`
- 鉴权：JWT（access/refresh）或 Cookie Session（二选一；建议 JWT）
- 统一响应：
```json
{ "code": 0, "message": "ok", "data": ... }
```
- 分页：
  - `page`/`page_size` 或 `cursor`（推荐 cursor，后续扩展更稳）
- 错误码（示例）：
  - 1001 未登录，1002 无权限
  - 2001 积分不足，2002 冻结失败
  - 3001 Provider 超时，3002 Provider 限流，3003 Provider 不可用
  - 4001 参数校验失败，4004 资源不存在
  - 5000 服务器错误

### 13.2 用户端主要接口清单
**Auth**
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/me`

**Workspace**
- `GET /api/workspaces`
- `POST /api/workspaces`
- `POST /api/workspaces/{id}/members/invite`
- `PATCH /api/workspaces/{id}/members/{member_id}`

**Upload/Asset**
- `POST /api/uploads/cos/credentials`
- `POST /api/assets/record`
- `GET /api/assets/{id}/download-url`
- `POST /api/products/{id}/assets/process`

**Product**
- `POST /api/products`
- `GET /api/products`
- `GET /api/products/{id}`
- `PATCH /api/products/{id}`

**Recipe/Pack/Template**
- `GET /api/recipes`
- `POST /api/recipes` / `POST /api/recipes/{id}/clone`
- `POST /api/recipes/{id}/versions`
- `GET /api/packs` / `POST /api/packs`
- `GET /api/poster-templates` / `POST /api/poster-templates`

**PromptDraft**
- `POST /api/prompt-drafts/compile`
- `PATCH /api/prompt-drafts/{id}`
- `POST /api/prompt-drafts/{id}/improve`

**Pricing**
- `POST /api/pricing/estimate`  *(建议新增)*

**Job**
- `POST /api/jobs`
- `GET /api/jobs/{id}`
- `GET /api/jobs/{id}/items`
- `POST /api/jobs/{id}/cancel`
- `GET /api/jobs/{id}/events`（SSE）

**Generation**
- `GET /api/generations`
- `GET /api/generations/{id}/tree`
- `POST /api/generations/{id}/iterate`
- `POST /api/generations/{id}/favorite`
- `POST /api/generations/{id}/set-style-anchor`

**Export**
- `POST /api/exports/zip`
- `GET /api/exports/{id}`

**Credits**
- `GET /api/credits/balance`
- `GET /api/credits/ledger`
- `POST /api/credits/recharge`（Owner/Admin）

### 13.3 管理端接口清单（SystemAdmin）
- Provider：`/api/admin/providers`
- Models：`/api/admin/provider-models`
- ModelGroups：`/api/admin/model-groups`
- Routing：`/api/admin/routing-policies`
- Pricing：`/api/admin/price-plans`、`/api/admin/price-rules`、`/api/admin/recharge-products`
- 全局配方发布/回滚：`/api/admin/recipes/*`（可选扩展）
- 审计查询：`/api/admin/audit-logs`
- 积分调整：`/api/admin/credits/adjust`

> 管理端所有写操作必须写 audit_logs。

---

## 14. 前端设计（React + Ant Design）

### 14.1 路由
- `/login`
- `/workspaces`（选择/创建）
- `/products`（列表）
- `/products/new`
- `/products/:id`（产品工作台）
- `/recipes`（配方中心）
- `/packs`（产物包）
- `/templates`（模板中心）
- `/credits`（积分与流水）
- `/admin/*`（系统管理员）

### 14.2 产品工作台（核心页面布局）
- 顶部：平台 Tabs（Amazon/抖音）+ 积分余额
- 左侧：产品结构化信息 + 素材列表（原图/cutout/mask 状态）
- 中间：Pack/分类选择 + 每类控制项（场景/氛围/光线/道具密度/张数/比例/分辨率）
- 右侧：PromptDraft 确认区（普通/高级）+ “预计扣费” + 开始生成
- 底部：分类瀑布流（流式状态、迭代、收藏、下载、设风格锚点）

### 14.3 SSE 处理
- 组件层建立 `useJobEvents(jobId)` hook：自动重连、断线补拉最新 job 状态
- UI 必须能展示：部分成功、失败原因、重试按钮（触发“重建 item”或“重新生成”）

### 14.4 Mask 编辑器
- Konva/Fabric 画布：涂抹/擦除/撤销
- 生成 mask PNG 上传 COS → 记录为 asset(type=mask) → 迭代接口引用 mask_asset_id

---

## 15. 管理后台（必须具备的页面）

1) **Provider 管理**：Key、启停、限流、健康指标、错误率
2) **模型目录**：能力标签、默认参数、参数范围、最大输出、启停
3) **模型组**：组内模型、权重、主备优先级
4) **路由策略**：按平台/分类/配方/类目/工作区匹配，配置主备模型组
5) **定价中心**：
   - 价格方案（版本发布/回滚）
   - 价格规则（match + formula 组件）
   - 价格预估器（选择条件即算预计积分）
6) **全局配方/模板发布**（可选但建议）
7) **审计日志**：按 workspace/用户/时间过滤
8) **全站任务监控**：失败率、队列堆积、耗时分布

---

## 16. 安全、合规、风控与限流

- COS：STS 临时凭证仅允许指定前缀；下载签名 URL 短期有效
- RBAC：workspace 维度严格校验（任何 product/job/generation 必须属于当前 workspace）
- 限流：
  - API：按用户/工作区做请求频率限制（可用 Redis sliding window）
  - 生成：按 provider/model/workspace/user 三层限流
- 审计：关键操作留痕
- 合规：平台规则（主图白底、禁宣词等）建议先做“提示 + 可配置阻断级别”，避免过度误杀。

---

## 17. 观测与运维（建议落地到可用）
- 日志：结构化 JSON，包含 request_id、user_id、workspace_id、job_id
- 指标：
  - provider 成功率/延迟/限流次数
  - job_item 失败原因分布
  - 队列长度与积压时间
  - 积分冻结与结算差异（对账）
- 告警：provider 连续失败、队列堆积、DB 连接耗尽、COS 上传失败

---

## 18. 部署与环境（腾讯云建议）
- 计算：CVM 或 TKE（K8s）
- 数据库：腾讯云 PostgreSQL（或自建）
- Redis：腾讯云 Redis
- COS：私有桶
- 域名与 HTTPS：CLB/Nginx + 证书
- Worker 横向扩容：按队列区分并发（图像/视频/渲染/导出）

环境变量（示例）
```bash
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
REDIS_URL=redis://:pass@host:6379/0
JWT_SECRET=...
COS_BUCKET=...
COS_REGION=...
COS_STS_SECRET_ID=...
COS_STS_SECRET_KEY=...
```

---

## 19. 测试策略
- 单元测试：pricing 引擎、路由选择、权限校验、账本幂等
- 集成测试：Job 创建→冻结→worker 执行→capture/release 全链路
- 契约测试：前后端接口 Schema 固化（避免联调扯皮）
- E2E：产品创建、上传、生成、迭代、导出
- 压测：单 workspace 日 100 张/用户，多用户并发下队列与限流表现

---

## 20. 局限性与风险边界（必须写入产品说明/UI 提示）
1) **多角度展示**：当用户仅提供 1 张图时，系统输出为“表现模式”，不承诺真实物理旋转结构。
2) **零部件/内部结构**：不凭空生成内部结构；默认只做标注与局部放大。
3) **使用型模特（上身/手持）**：若 provider 不支持遮挡/try-on，将自动降级为展示型模特并提示原因。
4) **视频**：三方波动大，必须保留动效降级交付。

---

## 21. 开发任务拆分与依赖顺序（不改变最终功能边界）
1) 基础：鉴权、Workspace、RBAC、审计
2) COS 上传与资产入库、资产处理（抠图三方 + 缩略图）
3) 配方/Pack/平台方案/品牌档案数据结构与管理页
4) Provider/模型中心 + 路由策略 + 限流组件（Redis 信号量）
5) 定价中心（price_plan/rule + estimate API）+ 积分账本（hold/capture/release 幂等）
6) Job/JobItem/Generation 全链路 + Celery 队列 + SSE
7) 迭代（mask 编辑、inpaint、版本树）
8) 模板渲染（海报/尺寸/参数/详情长图）
9) 视频链路 + 降级动效
10) 全站监控看板与告警

