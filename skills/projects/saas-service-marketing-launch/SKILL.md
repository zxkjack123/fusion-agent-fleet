---
name: "saas-service-marketing-launch"
description: "FormatForgeNet 新服务对外营销面上线 checklist: 当后端服务 (worker/API/计费) 已就绪后, 把服务暴露到用户面 (Home/Showcase/Pricing/Faq/changelog) + 部署上线. SaaS service marketing rollout, exposing backend-ready service to user-facing pages, naming consistency, boundary-statement audit, DB-driven changelog, two-tier nginx deploy, online regression matrix."
revision: 1
---

# SaaS Service Marketing Launch (FormatForgeNet)

> Crystallized from: deai-review-launch (AI味儿检测 上线, 2026-04-22)
> Date: 2026-04-22
> Trigger: T1 (≥5 工具步) + T3 (用户隐含确认)

## When to Use

- FormatForgeNet 已经接入了一个新的后端服务 (worker queue + API + 计费) 但**用户面 0 暴露**
- 用户需要：定一个产品名 + 决定上线状态 (内测/灰度/B 全量) + 把服务铺到所有营销面
- 涉及 Home / Showcase / Pricing / Faq / changelog 等多个 Vue 页面的协同改动
- 改动后需要构建 + 部署到 JP 节点 + 线上回归

## When NOT to Use

- 只是改后端逻辑、不动用户面 (用 `formatforgenet-deploy` 即可)
- 纯文案微调 (例如改一句副标题) — 直接编辑对应文件即可，无需走 checklist
- 新加的不是"对外服务"而是后台工具/管理页 (不需要进 Pricing/Faq)
- 非 FormatForgeNet 项目 (本 skill 的文件路径与组件结构是 FormatForgeNet 专属)

## Workflow

### Step 0: 上线前对齐 (必须先和用户确认)

- **产品名**：用户面统一叫什么？(可与 `service_id` 不同; 例如 `deai_review` → "AI味儿检测")
- **上线状态**：内测 / 灰度 / B 全量上线 → 决定是否在 Home 露出、是否进 Pricing 表
- **能力边界声明**：服务是否容易被误解？(例如 AI/检测/识别/打分类服务必须显式说明"非什么")
- **价格定档**：与后端 `credit_service.py` 中的积分一致

### Step 1: Convert.vue 服务选择器文案

文件：`docconv-saas/frontend/src/views/Convert.vue`

- 找到 `id: "<service_id>"` 服务对象，把 `label` / 描述 / 选项标签都改成新产品名
- 选项 (如 `doc_type` select) 保持后端键不变，仅改展示文本

### Step 2: 创建详情页 ShowcaseXxx.vue

文件：`docconv-saas/frontend/src/views/Showcase<ServiceName>.vue`

参考 `ShowcaseDeai.vue` 的 6 段结构：
1. 功能亮点
2. 处理流程
3. 输入/输出格式
4. 报告/产出示例
5. **能力边界**（明示"不是什么 / 不输出什么"）
6. 适用场景

加一个 `action-row` 引导用户去 `/convert?service=<service_id>`。

### Step 3: 路由注册

文件：`docconv-saas/frontend/src/router/index.ts`

```ts
import Showcase<X>View from "@/views/Showcase<X>.vue"
// ...
{ path: "/showcase/<x>", name: "showcase-<x>", component: Showcase<X>View }
```

### Step 4: 营销面批量铺设 (5 处)

| 文件 | 改动 |
|------|------|
| `views/Showcase.vue` | cards 数组追加新卡片 (icon + title + desc + tags + path) |
| `views/Home.vue` | features 行从 3 列 (`:md="8"`) 改 4 列 (`:md="6"`) 加新卡; diffItems 表加新行 |
| `views/Pricing.vue` | serviceCosts 数组追加 `{ name, input, output, cost }` |
| `views/Faq.vue` | 加 `el-collapse-item`, 标题用用户最容易误解的问题, 答案先说"不能/不是" |
| (DB) `update_logs` 表 | 写新公告: `version`, `title`, `content` (Markdown), `is_published=true`, `published_at=now()` |

DB 公告示例：
```bash
docker exec -i docconv-postgres psql -U <user> -d <db> << 'EOF'
INSERT INTO update_logs (version, title, content, is_published, published_at, created_at, updated_at)
VALUES ('v2026.04.22', '新服务上线：XXX', '我们上线了...', true, now(), now(), now());
EOF
```

### Step 5: 构建 + 部署

调用 `formatforgenet-deploy` skill。简化版：

```bash
cd docconv-saas/frontend && npm run build
# 或走 scripts/deploy-frontend.sh (含 scp)
bash scripts/deploy-frontend.sh
```

**Tailscale SSH** 可能需要重新认证，遇到 `Tailscale SSH requires an additional check` 暂停等用户。

### Step 6: 线上回归矩阵 (必跑全部 5 项)

```bash
# 1. 入口活着 + 无缓存
curl -sI https://formatforge.dev/ | grep -iE "HTTP|cache-control|cf-cache-status"

# 2. HTML 引用了新 bundle hash
curl -s https://formatforge.dev/ | grep -oE 'index-[A-Za-z0-9]+\.js'

# 3. 新 bundle 包含产品名
curl -s "https://formatforge.dev/assets/index-<HASH>.js" | grep -c "<产品名>"

# 4. 新详情页路由 OK (SPA fallback)
curl -s -o /dev/null -w "HTTP %{http_code}\n" https://formatforge.dev/showcase/<x>

# 5. changelog API 头条是新公告
curl -s "https://formatforge.dev/api/updates?limit=3" | head -c 600
```

5 项必须**全 PASS** 才算上线完成。

## Inputs & Outputs

| Input | Source |
|-------|--------|
| 后端 `service_id` 与计费档 | `backend/app/services/credit_service.py` |
| 产品名 + 上线状态 + 边界声明 | 用户口头确认 (Step 0) |
| 现有 Vue 页面结构 | `docconv-saas/frontend/src/views/` |

| Output | Format |
|--------|--------|
| 5 处用户面文件改动 + 1 个新详情页 + 1 条 DB 公告 | Vue/TS 文件 + PG 行 |
| 部署到 JP 节点的新 dist | `/var/www/formatforge/` (新 hash bundle) |
| 上线证据 | 线上回归 5 项 PASS 输出 |

## Common Pitfalls

- **产品名与 service_id 不一致**：用户面可以是中文/口语化的 (如 "AI味儿检测")，但**所有调用后端的地方** (Convert.vue 的 `id`, API URL `/services/deai_review`) 必须保持后端 ID。改名只改 label/title/desc。
- **能力边界没写**：检测/识别/AI 类服务**必须**在 ShowcaseXxx + Faq + changelog 三处显式声明"不是什么"，否则用户会期待错位 (如把"AI味儿检测"误以为是"AI 文本来源识别器")。
- **Home features 列数没调**：从 3 卡加到 4 卡时，Element Plus 的 `:md` 要从 8 改成 6，否则布局错位。
- **Pricing 的积分对不上后端**：`Pricing.vue` 的 `cost: "3 积分"` 必须等于 `credit_service.py` 中该服务的 `(base, deluxe, refund)` 元组的第一个值。
- **DB 公告漏 `is_published=true`**：忘了发布字段会导致 `/api/updates` 不返回新公告，前端公告位空白。
- **跳过线上回归**：构建成功不代表 CDN 拿到新 bundle。Cloudflare 边缘可能短暂缓存旧 HTML。回归矩阵第 2 步 (HTML 引用 hash 是否更新) 是关键防线。
- **没把后端服务先跑通就开始改前端**：本 skill 假设后端已经能处理任务并扣费。如果后端还没接好，请先完成 worker + API + service registry 注册，再回来跑此 checklist。

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-22 | Initial crystallization | deai-review-launch 上线 (Tasks 1.1–3.3, 7 commits) |
