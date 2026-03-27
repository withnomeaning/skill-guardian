# Skill Guardian 🛡️

**Your agent's immune system.** Vet skills before installing, scan what's already there, and sleep better at night.

**你的 Agent 免疫系统。** 装 Skill 之前先体检，装完了定期复查，晚上睡得更踏实。

---

## The Problem / 问题

The OpenClaw skill ecosystem is open — anyone can publish a skill. That's great for innovation, terrible for security. A skill that says "check the weather" could secretly read your SSH keys. A "markdown formatter" could phone home with your MEMORY.md.

OpenClaw 的 Skill 生态是开放的，谁都能发布。这对创新很好，对安全很糟。一个声称"查天气"的 Skill 可能在偷读你的 SSH 密钥，一个"Markdown 排版工具"可能把你的 MEMORY.md 悄悄传到外面。

**Skill Guardian catches these before they catch you.**

**Skill Guardian 在它们得手之前先逮住它们。**

---

## What It Does / 功能

### 🔍 Pre-install Review / 安装前审查

About to install a shiny new skill? Guardian reads every file, checks against 6 categories of red flags, and tells you what's actually going on under the hood.

想装一个新 Skill？Guardian 会通读所有文件，对照 6 大类红线检查，告诉你引擎盖下面到底在搞什么。

### 📡 Batch Scan / 已装批量扫描

```bash
python3 scripts/scan_skills.py
```

Scans every installed skill in one shot. Example output:

一键扫描所有已装 Skill。输出示例：

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

> Looks scary? Not really — bing-search *needs* network access to search. That's the point: Guardian flags everything, then your agent (or you) decides what's legit.
>
> 看着挺吓人？其实还好 — 搜索 Skill *当然*需要联网。Guardian 的逻辑是：先全标出来，再由你（或你的 Agent）判断哪些是正常操作。

### 🏠 Workspace Audit / 工作区审计

```bash
python3 scripts/audit_workspace.py
```

Checks your SOUL.md, MEMORY.md, USER.md and other config files for:

检查你的配置文件：

- ✅ Is SOUL.md properly locked down? / SOUL.md 安全配置齐全吗？
- 🔑 Any plaintext passwords/tokens/keys? / 有没有明文密码、Token、密钥？
- 📁 Unexpected executable files? / 有没有意外的可执行文件？
- 🔒 File permissions look right? / 文件权限对不对？

```json
{
  "soul_audit": {
    "checks": [
      { "name": "注入防御规则", "pass": true },
      { "name": "敏感路径黑名单", "pass": true },
      { "name": "反泄露规则", "pass": true },
      { "name": "文件保护铁律", "pass": true }
    ],
    "score": 4,
    "total": 5
  },
  "secrets_found": []
}
```

### 🚨 Security Patrol / 综合巡检

Scan + Audit in one go. Say "安全巡检" or "security patrol" and your agent runs the full suite.

扫描 + 审计一步到位。跟你的 Agent 说"安全巡检"就行。

---

## Red Flags / 红线检测

| Category / 类别 | What it catches / 检测什么 |
|---------|-------------|
| 🌐 Network / 网络外传 | Undeclared `curl`, `fetch`, WebSocket to unknown URLs / 未声明的网络请求 |
| 🔑 Credentials / 凭证窃取 | Reading `~/.ssh/`, `~/.aws/`, API keys / 读取密钥和凭证 |
| 🧠 Memory / 记忆窃取 | Accessing MEMORY.md, USER.md, SOUL.md / 偷读 Agent 记忆文件 |
| 🎭 Obfuscation / 代码混淆 | `eval()` + external input, base64 execution / 动态执行和混淆代码 |
| ⚙️ System / 系统权限 | `sudo`, `/etc/` mods, crontab / 系统级权限操作 |
| 👻 Stealth / 隐蔽行为 | Undeclared background processes, telemetry / 后台进程和遥测 |

## Risk Levels / 风险等级

| Level / 等级 | Meaning / 含义 |
|-------|---------|
| 🟢 Low / 低 | Clean — no scripts, no network, no file access / 干净，纯文本指令 |
| 🟡 Medium / 中 | Uses network/files, but behavior matches what it claims / 有网络和文件操作，但和声明一致 |
| 🔴 High / 高 | Touches credentials/system, or does things it didn't declare / 涉及凭证或系统，或有未声明行为 |
| ⛔ Extreme / 极端 | Core intent looks malicious / 核心意图就是恶意的 |

---

## Install / 安装

### Via ClawHub

```bash
clawhub install skill-guardian
```

### Manual / 手动

```bash
git clone https://github.com/withnomeaning/skill-guardian.git ~/.openclaw/skills/skill-guardian
```

---

## File Structure / 文件结构

```
skill-guardian/
├── SKILL.md                        # Agent instructions / Agent 指令
├── scripts/
│   ├── scan_skills.py              # Batch scanner / 批量扫描器
│   └── audit_workspace.py          # Workspace auditor / 工作区审计
└── references/
    └── red-flags-patterns.md       # Detailed patterns & criteria / 红线模式和判断标准
```

## Design Philosophy / 设计理念

- **Flag everything, judge in context** — A search skill using `urllib` is fine. A "formatter" using `urllib` is sus. / 先全标，再看上下文判断
- **Transparent** — Every flag comes with reasoning, no black box / 每个标记都给理由，不搞黑箱
- **Human-in-the-loop** — 🔴+ always needs your approval / 高风险必须你拍板
- **Read-only** — Guardian only reads, never modifies / 只读不写
- **Zero dependencies** — Python 3.6+ standard library only / 零第三方依赖

## Requirements / 依赖

- Python 3.6+
- That's it. No pip install, no npm, no nothing. / 就这，不用装任何东西

## License

MIT

## Author

[@withnomeaning](https://github.com/withnomeaning)
