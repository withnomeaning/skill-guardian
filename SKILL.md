---
name: skill-guardian
description: |
  AI Agent 安全守卫：安装 Skill 前的深度安全审查、已装 Skill 批量扫描、workspace 配置安全审计、综合安全巡检。
  Use when: 用户提到安装新 skill、审查 skill、vet skill、检查 skill 安全性、扫描已装 skill、workspace 安全审计、安全巡检、security check、security audit。也适用于用户说"这个 skill 安全吗"、"帮我看看能不能装"、"扫一下我的 skill"等模糊表达。
  NOT for: 一般安全配置建议（写在 SOUL.md）、代码审计、漏洞扫描。
---

# Skill Guardian 🛡️

安全守卫，四个模块：安装前审查 → 已装扫描 → workspace 审计 → 综合巡检。

## 模块一：Skill 安装前审查

当用户要装新 skill 或要求审查某个 skill 时触发。

### 审查三步走

**1. 来源验证**

判断信任层级（从高到低）：
- OpenClaw 官方内置 → 低警惕
- ClawHub 高星(1000+)、已知作者 → 中等警惕
- ClawHub 新发布、低星、未知作者 → 高警惕
- 第三方平台/镜像站/直接 URL → 最高警惕，默认不信任

关键：只认 `clawhub.ai` 官方域名。镜像站是恶意 skill 重灾区，因为它们不受官方审核流程约束。任何要求交出凭证的 skill，无论来源都需人工审批。

**2. 代码深度审查**

通读 skill 所有文件（SKILL.md、scripts/、references/、assets/），对照红线清单逐项排查。

红线分六类（命中任何一条即标记）：

| 类别 | 关注什么 | 为什么危险 |
|------|----------|-----------|
| A. 网络外传 | curl/wget/fetch 到不明 URL、IP 直连、未声明的 WebSocket | 可能在偷偷把你的数据发出去 |
| B. 凭证窃取 | 读取 API key/token/密码、访问 ~/.ssh/ ~/.aws/ 等 | 拿到凭证就能冒充你 |
| C. 记忆窃取 | 读取 MEMORY.md/USER.md/SOUL.md/memory/ 目录 | 新型攻击：偷走你的 agent 人格和私人信息 |
| D. 代码混淆 | eval()+外部输入、base64 解码执行、混淆代码块 | 藏恶意代码最常用的手法 |
| E. 系统权限 | sudo、修改 /etc/、改 crontab/shell 配置 | 可能永久改变你的系统 |
| F. 隐蔽行为 | 未声明的后台进程、静默遥测、修改其他 skill | 做了不告诉你的事最可怕 |

需要具体的 grep 模式和判断标准时，读 `references/red-flags-patterns.md`。

**3. 意图一致性分析**

最容易被忽视但最有价值的一步：代码实际做的事 vs 文档声称的功能是否一致？一个"天气查询 skill"如果在读 SSH 密钥，那就是挂羊头卖狗肉。检查：
- description 声称的能力 vs 文件中的实际操作
- 是否存在未声明的"附带"行为
- 文件名/变量名是否有误导性（如 `helper.py` 实际做数据外传）

### 风险定级

| 等级 | 条件 | 建议 |
|------|------|------|
| 🟢 低 | 纯指令/文本，无网络/文件/脚本 | 可装 |
| 🟡 中 | 涉及文件操作、浏览器、外部 API，但行为与声明基本一致 | 完整审查，告知风险点 |
| 🔴 高 | 涉及凭证、系统设置、大范围文件访问，或核心功能正常但夹带未声明行为 | 必须人工审批 |
| ⛔ 极端 | 核心意图就是恶意的（窃取数据、植入后门、伪装身份），或多条红线同时命中且无合理解释 | 不安装，说明原因 |

**定级原则**：不是"命中红线就⛔"。关键看**意图和影响范围**：
- 核心功能正常+夹带未声明遥测 → 🔴高风险（可修复后使用），不是⛔
- 核心功能正常+需要网络但已声明 → 🟡中风险，不因功能需要的网络访问升级
- 核心功能就是恶意的/伪装身份 → ⛔极端
- 红线命中数量不是唯一标准，一个"curl到不明IP+读SSH密钥+装crontab"比十个"未声明写入json文件"严重得多

### 输出格式

报告应包含：Skill 基本信息（名称/来源/作者/版本/星数）→ 红线检查结果（逐条列出命中项）→ 权限需求摘要（读/写/网络/命令）→ 意图一致性判断 → 风险等级 → 结论与建议。保持简洁，有问题的地方详细说，没问题的一笔带过。

---

## 模块二：已装 Skill 批量扫描

对 `~/.openclaw/skills/` 下所有已安装 skill 执行自动化安全扫描。

**触发**："扫描所有已装skill"、"scan installed skills"

**执行**：运行 `scripts/scan_skills.py`（自动排除 skill-guardian 自身），它会扫描所有 skill 文件中的红线模式匹配，输出 JSON 报告。

```bash
python3 <skill-guardian-path>/scripts/scan_skills.py
```

脚本只做模式匹配，不做语义判断。拿到结果后，结合上下文分析每个命中项是否是合理操作（比如 `127.0.0.1` 是本地 CDP 连接、`base64` 用于图片解码），还是真正的安全隐患。输出按风险等级分组的总览报告。

扫描单个 skill：
```bash
python3 <skill-guardian-path>/scripts/scan_skills.py <skill-name-or-path>
```

---

## 模块三：Workspace 安全审计

检查 workspace 配置文件（SOUL.md/MEMORY.md/USER.md/AGENTS.md 等）的安全性。

**触发**："检查workspace安全"、"audit workspace"

**执行**：运行 `scripts/audit_workspace.py`，它会检查：
- SOUL.md 安全配置完整性（身份验证、注入防御、敏感路径、反泄露、文件保护）
- AGENTS.md 安全原则完整性
- 所有 .md 文件中的明文敏感信息（密码、API key、token、私钥）
- workspace 中意外的可执行文件
- 文件/目录权限

```bash
python3 <skill-guardian-path>/scripts/audit_workspace.py
```

拿到 JSON 结果后，解读并给出具体改进建议。

---

## 模块四：综合安全巡检

一次性执行模块二 + 模块三，适合定期检查。

**触发**："安全巡检"、"security patrol"

依次运行两个脚本，汇总分析，输出综合报告。

---

## 核心原则

- **宁严勿松** — 误报可以解释，漏报可能造成真实损害
- **透明** — 每个判断都说理由，不搞黑箱
- **人工兜底** — 🔴及以上必须用户决定，agent 不自作主张
- **只读** — 本 skill 只分析，绝不修改任何文件
- **自身安全** — 纯指令+本地脚本，不联网，不访问敏感路径
