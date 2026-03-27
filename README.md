# Skill Guardian 🛡️

You're about to install a skill that says it "checks the weather."

It also reads `~/.ssh/`, curls to a random IP, and runs `eval()` on the response.

Good luck with that.

---

Skill Guardian vets OpenClaw skills before you install them, and scans the ones you already have. It checks code against 6 categories of red flags, audits your workspace config files, and tells you exactly what's going on — with reasoning, not just yes/no.

## ⚡ Quick Start

```bash
# Install
git clone https://github.com/withnomeaning/skill-guardian.git ~/.openclaw/skills/skill-guardian

# Scan all installed skills
python3 ~/.openclaw/skills/skill-guardian/scripts/scan_skills.py

# Audit your workspace
python3 ~/.openclaw/skills/skill-guardian/scripts/audit_workspace.py
```

Once installed, your agent uses it automatically — say "scan my skills" or "安全巡检" and it runs.

## 🔍 What It Catches

| Category | What it flags |
|----------|--------------|
| 🌐 Network | Undeclared `curl`, `fetch`, WebSocket to unknown URLs |
| 🔑 Credentials | Reading `~/.ssh/`, `~/.aws/`, API keys, tokens |
| 🧠 Memory theft | Accessing `MEMORY.md`, `USER.md`, `SOUL.md` |
| 🎭 Obfuscation | `eval()` + external input, base64-decoded execution |
| ⚙️ System | `sudo`, `/etc/` modifications, crontab changes |
| 👻 Stealth | Undeclared background processes, silent telemetry |

## 📊 Four Modules

### Pre-install Review

Triggered automatically when you're about to install a new skill. Reads every file, checks against red flags, analyzes whether the code actually does what the docs claim.

Source verification → deep code review → intent consistency analysis → risk rating.

### Batch Scan

```bash
python3 scripts/scan_skills.py
```

One command, all installed skills scanned. Output:

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

Looks terrifying — but bing-search *needs* network access to search. The scanner flags everything by pattern matching; your agent (or you) decides what's legit in context.

Scan a single skill:

```bash
python3 scripts/scan_skills.py <skill-name-or-path>
```

### Workspace Audit

```bash
python3 scripts/audit_workspace.py
```

Checks your configuration files for:
- SOUL.md security coverage (injection defense, sensitive paths, anti-leak rules)
- Plaintext passwords, API keys, tokens in any `.md` file
- Unexpected executable files in workspace
- File and directory permissions

```json
{
  "soul_audit": {
    "score": 4,
    "total": 5,
    "checks": [
      { "name": "Injection defense", "pass": true },
      { "name": "Sensitive path blocklist", "pass": true },
      { "name": "Anti-leak rules", "pass": true },
      { "name": "File protection", "pass": true },
      { "name": "Identity verification", "pass": false }
    ]
  },
  "secrets_found": []
}
```

### Security Patrol

Scan + Audit in one go. Tell your agent "security patrol" and it runs the full suite.

## ⚖️ Risk Levels

| Level | Meaning |
|-------|---------|
| 🟢 Low | Pure text instructions, no scripts/network/file access |
| 🟡 Medium | Uses network or files, but behavior matches what it claims |
| 🔴 High | Touches credentials or system config, or has undeclared behavior |
| ⛔ Extreme | Core intent looks malicious |

Flagging ≠ conviction. A search tool using `urllib` is fine. A "markdown formatter" using `urllib` deserves questions. Context matters.

## 📁 Structure

```
skill-guardian/
├── SKILL.md                        # Agent instructions (Chinese)
├── scripts/
│   ├── scan_skills.py              # Batch scanner (~180 lines)
│   └── audit_workspace.py          # Workspace auditor (~160 lines)
└── references/
    └── red-flags-patterns.md       # Detailed grep patterns & judgment criteria
```

## Design

- **Flag everything, judge in context** — false positives can be explained, false negatives cause real harm
- **Transparent** — every flag comes with reasoning
- **Human-in-the-loop** — 🔴+ always needs user approval
- **Read-only** — never modifies any file
- **Zero dependencies** — Python 3.6+ stdlib only

## 📦 Install

```bash
# ClawHub
clawhub install skill-guardian

# Manual
git clone https://github.com/withnomeaning/skill-guardian.git ~/.openclaw/skills/skill-guardian
```

## License

MIT — [@withnomeaning](https://github.com/withnomeaning)
