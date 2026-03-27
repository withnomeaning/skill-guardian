# Skill Guardian 🛡️

OpenClaw 的 skill 生态是开放的，谁都能发布。这很好，但也意味着你装的那个 skill 可能不只是在"查天气"——它可能顺手读了你的 SSH 密钥。

Skill Guardian 就干一件事：在你装 skill 之前帮你查清楚它到底在搞什么。装完的也能回头扫一遍。

## 四个模块

### 🔍 安装前审查

要装新 skill 时自动触发。通读 skill 所有文件，对照 6 大类红线检查，判断代码实际行为和文档声称的功能是否一致。

审查流程：来源验证 → 代码深度审查 → 意图一致性分析 → 风险定级。

### 📡 已装批量扫描

```bash
python3 scripts/scan_skills.py
```

一键扫描 `~/.openclaw/skills/` 下所有已装 skill。输出示例：

```json
{
  "name": "bing-search",
  "files_scanned": 2,
  "total_hits": 8,
  "hits_by_category": {
    "A_network_external": 5,
    "C_memory_files": 1,
    "D_obfuscation": 1,
    "E_system_privilege": 1
  },
  "risk_level": "⛔ EXTREME"
}
```

看着吓人，但 bing-search 本来就需要联网才能搜索。脚本只做模式匹配不做语义判断，标出来之后由 agent 或你自己判断哪些是正常操作。

也可以扫单个：

```bash
python3 scripts/scan_skills.py <skill名称或路径>
```

### 🏠 Workspace 审计

```bash
python3 scripts/audit_workspace.py
```

检查 workspace 配置文件的安全状况：

- SOUL.md 安全配置是否齐全（注入防御、敏感路径黑名单、反泄露规则等）
- 所有 .md 文件里有没有明文密码、API key、token
- 有没有意外的可执行文件
- 文件和目录权限是否合理

```json
{
  "soul_audit": {
    "score": 4,
    "total": 5,
    "checks": [
      { "name": "注入防御规则", "pass": true },
      { "name": "敏感路径黑名单", "pass": true },
      { "name": "反泄露规则", "pass": true },
      { "name": "文件保护铁律", "pass": true },
      { "name": "身份验证机制", "pass": false }
    ]
  },
  "secrets_found": []
}
```

### 🚨 综合巡检

模块 2 + 3 一起跑。跟你的 agent 说"安全巡检"就行。

## 🚩 红线检测（6 类）

| 类别 | 查什么 |
|------|--------|
| 🌐 网络外传 | 未声明的 `curl`、`fetch`、WebSocket 到不明 URL |
| 🔑 凭证窃取 | 读取 `~/.ssh/`、`~/.aws/`、API key、token |
| 🧠 记忆窃取 | 访问 MEMORY.md、USER.md、SOUL.md 等 agent 记忆文件 |
| 🎭 代码混淆 | `eval()` + 外部输入、base64 解码执行、混淆代码 |
| ⚙️ 系统权限 | `sudo`、修改 `/etc/`、改 crontab |
| 👻 隐蔽行为 | 未声明的后台进程、遥测上报 |

详细的 grep 模式和判断标准在 `references/red-flags-patterns.md`。

## 📊 风险等级

| 等级 | 含义 |
|------|------|
| 🟢 低 | 纯文本指令，没有脚本/网络/文件操作 |
| 🟡 中 | 有网络和文件操作，但和声明的功能一致 |
| 🔴 高 | 涉及凭证或系统配置，或有未声明的行为 |
| ⛔ 极端 | 核心意图就是恶意的 |

定级不是"命中红线就判死刑"。一个搜索工具用 `urllib` 是正常的，一个"Markdown 排版工具"用 `urllib` 就值得追问了。关键看意图和上下文。

## 📦 安装

```bash
# ClawHub
clawhub install skill-guardian

# 手动
git clone https://github.com/withnomeaning/skill-guardian.git ~/.openclaw/skills/skill-guardian
```

## 📁 文件结构

```
skill-guardian/
├── SKILL.md                        # Agent 指令
├── scripts/
│   ├── scan_skills.py              # 批量扫描（~180 行）
│   └── audit_workspace.py          # 工作区审计（~160 行）
└── references/
    └── red-flags-patterns.md       # 红线模式和判断标准
```

## ⚖️ 设计原则

- 先全标出来，再看上下文判断——误报可以解释，漏报可能出事
- 每个标记都给理由，不搞黑箱
- 🔴 及以上必须用户拍板，agent 不自作主张
- 只读不写，不修改任何文件
- 零依赖，Python 3.6+ 标准库就够

## License

MIT — [@withnomeaning](https://github.com/withnomeaning)
