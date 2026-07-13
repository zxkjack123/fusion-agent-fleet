# Skill Index — 技能目录

33个已固化的技能，按领域分类。每个技能在 `skills/<name>/SKILL.md` 中有完整的工作流、使用条件、常见陷阱和修订日志。

## Agent Fleet Governance & Infrastructure

| Skill | 用途 | 何时使用 |
|-------|------|----------|
| [agent-contract-rollout](skills/agent-contract-rollout/SKILL.md) | 批量注入委派合同和出站委派 schema | 新增 agent 或修改 agent 间调用关系时 |
| [agent-fleet-boundary-cleanup](skills/agent-fleet-boundary-cleanup/SKILL.md) | Agent 角色边界澄清 + T1/T2/T3 工具分级 | 多个 agent 角色重叠、工具所有权混乱时 |
| [agent-fleet-governance-update](skills/agent-fleet-governance-update/SKILL.md) | 模型分流重平衡 + 静态校验 + 文档治理 | 引入新模型层、升级校验脚本时 |
| [agent-iterative-refinement](skills/agent-iterative-refinement/SKILL.md) | 单个 agent 的渐进式改进（A1, A2... 编号任务 + 独立 commit） | 根据使用反馈迭代优化 agent 定义 |
| [agent-orchestration-audit](skills/agent-orchestration-audit/SKILL.md) | 编排器 agent 的"能力感知盲区"检测和修复 | 编排器声明了子代理但工作流中从未调用 |
| [agent-tool-budget-trim](skills/agent-tool-budget-trim/SKILL.md) | 128 工具硬上限治理：wildcard→allow-list 转换 + 预算脚本 | 工具数接近或超过 128 上限时 |
| [arch-spec-multi-file-rollout](skills/arch-spec-multi-file-rollout/SKILL.md) | 架构设计文档到代码的批量落地 | 有 `docs/<arch>.md` 需要改多类文件时 |
| [deep-lint-pipeline](skills/deep-lint-pipeline/SKILL.md) | 全链路文稿质量检查流水线 | 含参考文献的稿件提交前全面检查 |
| [repo-modernization-rollout](skills/repo-modernization-rollout/SKILL.md) | 分波治理升级：宪章、失败记忆、slash prompt、评分体系 | Agent 仓库大规模现代化改造 |

## Scientific Computing & Data Science

| Skill | 用途 | 何时使用 |
|-------|------|----------|
| [pymatgen-materials](skills/pymatgen-materials/SKILL.md) | **🆕** 材料科学工具包 — 晶体结构、相图、Materials Project 集成 | 核材料筛选、辐照损伤前处理、包层材料热力学 |
| [deepchem-ml](skills/deepchem-ml/SKILL.md) | **🆕** 分子机器学习 — 性质预测、GNN、迁移学习 | 辐照产物性质预测、冷却剂化学分析、腐蚀产物识别 |
| [scikit-learn-ml](skills/scikit-learn-ml/SKILL.md) | **🆕** 通用机器学习 — 分类/回归/聚类/降维 | 仿真结果分类、TBR 回归预测、参数聚类分析 |
| [matplotlib-seaborn-viz](skills/matplotlib-seaborn-viz/SKILL.md) | **🆕** 出版级科研图表 — 中子能谱、TBR 灵敏度图、活化时间演化 | 论文/报告/演示文稿的仿真数据可视化 |
| [networkx-analysis](skills/networkx-analysis/SKILL.md) | **🆕** 图/网络分析 — 核素衰变链、核数据依赖图、工作流 DAG | 衰变网络可视化、仿真工作流优化 |
| [polars-data](skills/polars-data/SKILL.md) | **🆕** 高性能数据处理 — 表达式 API、惰性评估、Arrow 互操作 | 大规模 tally 数据处理、核数据库批量查询 |
| [experimental-design](skills/experimental-design/SKILL.md) | **🆕** 实验/仿真设计(DOE) — 因子设计、响应面、拉丁超立方 | 包层参数 DOE 设计、屏蔽层优化、活化实验随机化 |
| [figure-style-migration](skills/figure-style-migration/SKILL.md) | **🆕** 图表风格迁移 — vision MCP 提取目标风格 + PaperBanana/tikz-writer 复现 | 适配特定期刊图表风格、保持论文视觉一致性 |
| [persistent-research-memory](skills/persistent-research-memory/SKILL.md) | **🆕** 持久化研究记忆 — 跨 session 知识图谱、上下文检索、记忆蒸馏 | 开始新 session 时加载先前研究上下文、结束时蒸馏发现 |

## Journal Submission Packs

| Skill | 用途 | 何时使用 |
|-------|------|----------|
| [fed-journal](skills/journals/fed-journal/SKILL.md) | **🆕** FED 期刊投稿包 — Elsevier 格式、双栏可选手稿、Cover Letter | 向 Fusion Engineering and Design 投稿时 |
| [nf-journal](skills/journals/nf-journal/SKILL.md) | **🆕** NF 期刊投稿包 — IOP 格式、LaTeX 模板、独立图表文件 | 向 Nuclear Fusion 投稿时 |
| [fst-journal](skills/journals/fst-journal/SKILL.md) | **🆕** FST 期刊投稿包 — ANS 格式、双盲可选、数据可用性声明 | 向 Fusion Science and Technology 投稿时 |
| [sofe-journal](skills/journals/sofe-journal/SKILL.md) | **🆕** SOFE 会议投稿包 — IEEE 双栏、6 页限制、PDF 兼容性 | 向 IEEE SOFE 会议投稿时 |
| [ansi-ans-journal](skills/journals/ansi-ans-journal/SKILL.md) | **🆕** ANS 系列期刊投稿包 (NT/NSE/FT) — ANS LaTeX 模板、SI 单位强制 | 向 ANS 系列期刊投稿时 |
| [mlst-journal](skills/journals/mlst-journal/SKILL.md) | **🆕** MLST 期刊投稿包 (IOP OA) — 多学科 ML、代码/数据补充 | 向 Machine Learning: Science and Technology 投稿时 |

## Nuclear Engineering & Simulation

| Skill | 用途 | 何时使用 |
|-------|------|----------|
| [fusion-magnet-heating-normalization](skills/fusion-magnet-heating-normalization/SKILL.md) | TF/PF 线圈核热归一化和 tally 范围审计 | 磁体核热计算结果需要校验时 |
| [parametric-sweep](skills/parametric-sweep/SKILL.md) | 参数扫描矩阵设计 + HPC 批量提交 + 结果聚合 | 需要扫参数做灵敏度分析时 |
| [hypothesis-generation](skills/hypothesis-generation/SKILL.md) | 结构化假说生成和评估（7 维度） | 需要从观测中产生竞争性假说时 |
| [literature-band-validation-suite](skills/literature-band-validation-suite/SKILL.md) | 数值模型 vs 文献参考带的比对验证 | 仿真结果需要与已发表数据比对时 |
| [scientific-troubleshooting](skills/scientific-troubleshooting/SKILL.md) | **🆕** 仿真结果/实验数据异常时的 5 阶段诊断方法 | 结果物理不合理、数据矛盾、"看起来不对"时 |
| [mcnp-native-plot-only](skills/mcnp-native-plot-only/SKILL.md) | MCNP6 原生几何绘图工作流 | 需要从大 MCNP 输入中提取局部几何截图时 |
| [sugon-mcnp6-apptainer](skills/sugon-mcnp6-apptainer/SKILL.md) | 曙光 HPC 上 Apptainer 容器化 MCNP6 运行 | 在曙光集群上提交 MCNP 作业时 |
| [sugon-mcnp6-gfortran-sif](skills/sugon-mcnp6-gfortran-sif/SKILL.md) | Hygon C86 上 gfortran 编译的 MCNP6 部署 | 在曙光 HB 集群上运行时 |

## Scientific Writing & Publishing

| Skill | 用途 | 何时使用 |
|-------|------|----------|
| [manuscript-figure-package-rebuild](skills/manuscript-figure-package-rebuild/SKILL.md) | 稿件图表单位修复和投稿包重建 | 图表 colorbar/axis 单位需要与正文对齐时 |
| [tikz-track-e](skills/tikz-track-e/SKILL.md) | TikZ 确定性 .tex 编辑操作 | 需要 swap/reroute/inline 编辑 TikZ 坐标时 |
| [track-e-tex-editing](skills/track-e-tex-editing/SKILL.md) | TikZ 坐标精确空间控制 | 需要多列/蛇形/网格布局的 TikZ 编辑时 |

## 跨仓库与科研工作流

| Skill | 用途 | 何时使用 |
|-------|------|----------|
| [cross-repo-guardrail](skills/cross-repo-guardrail/SKILL.md) | **🆕** 将 guardrail 推广到外部仓库 | 需要在外部仓库上运行物理合理性检查时 |
| [research-workflow-template](skills/research-workflow-template/SKILL.md) | **🆕** 6 阶段科研流程模板 | 开始新的科研项目或计算任务时 |

## Project Management

| Skill | 用途 | 何时使用 |
|-------|------|----------|
| [pm-excel-task-sync](skills/pm-excel-task-sync/SKILL.md) | Excel 任务表 → PM 系统安全同步 | 需要将 Excel 任务同步到 PM 数据库时 |

## SaaS / Deployment (project-specific)

| Skill | 用途 | 何时使用 |
|-------|------|----------|
| [formatforgenet-deploy](skills/projects/formatforgenet-deploy/SKILL.md) | FormatForgeNet 分拓扑部署 | 部署 FormatForgeNet 前后端时 |
| [saas-service-marketing-launch](skills/projects/saas-service-marketing-launch/SKILL.md) | SaaS 新服务营销上线 checklist | 新后端服务需要暴露到用户面时 |

## 按使用频率排序（Top 10）

1. **agent-iterative-refinement** — Agent 迭代优化最常用
2. **deep-lint-pipeline** — 稿件预提交检查最常用
3. **parametric-sweep** — 参数扫描最常用
4. **fusion-magnet-heating-normalization** — 磁体加热校验高频使用
5. **sugon-mcnp6-apptainer** — HPC 作业提交高频使用
6. **agent-tool-budget-trim** — 工具预算治理周期性使用
7. **agent-orchestration-audit** — 编排器审计周期性使用
8. **arch-spec-multi-file-rollout** — 架构落地按需使用
9. **manuscript-figure-package-rebuild** — 投稿前图表修复按需使用
10. **agent-contract-rollout** — 合同注入按需使用

---

*自动生成于 skill-crystallization pipeline。更新技能时请同步更新此索引。*
