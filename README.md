# Skill Guardian 🛡️

Security vetting for AI agent skills — audit before you install.

An [OpenClaw](https://github.com/openclaw/openclaw) skill that acts as your agent's immune system: **deep-review skills before installation, batch-scan installed skills, audit workspace configs, and run comprehensive security patrols.**

## Why

The OpenClaw skill ecosystem is open — anyone can publish a skill. That's powerful, but also risky. A skill that claims to "check the weather" could secretly read your SSH keys. Skill Guardian helps your agent detect these threats autonomously.

## Features

| Module | What it does |
|--------|-------------|
| **Pre-install Review** | Deep-reviews a skill's source, code, and intent before installation |
| **Installed Scan** | Batch-scans all installed skills against red-flag patterns |
| **Workspace Audit** | Checks SOUL.md, MEMORY.md, and other config files for security issues |
| **Security Patrol** | Runs scan + audit together for periodic checkups |

### Red Flag Detection (6 categories)

| Category | Examples |
|----------|---------|
| 🌐 Network exfiltration | Undeclared `curl`, `fetch`, WebSocket to unknown URLs |
| 🔑 Credential theft | Reading `~/.ssh/`, `~/.aws/`, API keys, tokens |
| 🧠 Memory theft | Accessing `MEMORY.md`, `USER.md`, `SOUL.md` |
| 🎭 Code obfuscation | `eval()` + external input, base64-decoded execution |
| ⚙️ System privilege | `sudo`, modifying `/etc/`, crontab changes |
| 👻 Stealth behavior | Undeclared background processes, silent telemetry |

### Risk Levels

| Level | Meaning |
|-------|---------|
| 🟢 Low | Pure instructions/text, no network/file/script access |
| 🟡 Medium | File/browser/API access, but behavior matches declaration |
| 🔴 High | Credential/system access, or undeclared side behaviors |
| ⛔ Extreme | Core intent is malicious (data theft, backdoor, identity spoofing) |

## Install

### Via ClawHub (recommended)

```bash
clawhub install skill-guardian
```

### Manual

```bash
git clone https://github.com/withnomeaning/skill-guardian.git ~/.openclaw/skills/skill-guardian
```

## Usage

Once installed, your OpenClaw agent will automatically use Skill Guardian when:

- You ask to install a new skill → **Pre-install review triggers**
- You say "scan my skills" → **Batch scan runs**
- You say "audit workspace" → **Workspace audit runs**
- You say "security patrol" → **Full patrol runs**

### CLI (standalone)

```bash
# Scan all installed skills
python3 scripts/scan_skills.py

# Scan a specific skill
python3 scripts/scan_skills.py <skill-name-or-path>

# Audit workspace
python3 scripts/audit_workspace.py
```

## File Structure

```
skill-guardian/
├── SKILL.md                          # Agent instructions
├── README.md                         # This file
├── LICENSE                           # MIT
├── scripts/
│   ├── scan_skills.py                # Batch scanner (~180 lines)
│   └── audit_workspace.py           # Workspace auditor (~160 lines)
└── references/
    └── red-flags-patterns.md         # Detailed grep patterns & judgment criteria
```

## Design Philosophy

- **Strict by default** — False positives can be explained; false negatives cause real harm
- **Transparent** — Every judgment comes with reasoning, no black boxes
- **Human-in-the-loop** — 🔴 and above always require user approval
- **Read-only** — This skill only analyzes, never modifies any files
- **Self-secure** — Pure instructions + local scripts, no network access, no sensitive path access

## Requirements

- Python 3.6+
- No third-party dependencies

## License

MIT

## Author

[@withnomeaning](https://github.com/withnomeaning)
