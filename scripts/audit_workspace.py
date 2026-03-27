#!/usr/bin/env python3
"""
Skill Guardian - Workspace 安全审计脚本
检查 workspace 配置文件中的安全隐患。
输出 JSON 报告供 Agent 解读。
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")

# 明文敏感信息模式
SENSITIVE_PATTERNS = [
    (r'(?i)password\s*[:=]\s*\S+', "明文密码"),
    (r'(?i)api[_-]?key\s*[:=]\s*["\']?\w{16,}', "API Key"),
    (r'(?i)secret\s*[:=]\s*["\']?\w{16,}', "Secret"),
    (r'(?i)token\s*[:=]\s*["\']?\w{16,}', "Token"),
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API Key 格式"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
    (r'xoxb-[a-zA-Z0-9-]+', "Slack Bot Token"),
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "私钥"),
]

# SOUL.md 应包含的安全配置
SOUL_CHECKLIST = [
    ("身份验证机制", [r'open_?id', r'sender_?id', r'owner.*identity', r'验证']),
    ("注入防御规则", [r'inject', r'注入', r'忽略.*规则', r'override.*rules', r'ignore.*instruction']),
    ("敏感路径黑名单", [r'\.ssh', r'\.aws', r'\.gnupg', r'restricted.*path', r'敏感路径']),
    ("反泄露规则", [r'anti.?leak', r'反泄露', r'密钥.*输出', r'不.*外泄']),
    ("文件保护铁律", [r'铁律', r'绝不.*删除', r'不.*修改']),
]

# AGENTS.md 应包含的安全配置
AGENTS_CHECKLIST = [
    ("安全原则", [r'安全', r'security']),
    ("群聊行为规则", [r'群聊', r'group.*chat']),
    ("外发操作限制", [r'外发', r'external', r'公开发布']),
]


def check_file_for_secrets(filepath: str) -> list:
    """检查文件中是否有明文敏感信息。"""
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except (IOError, OSError):
        return findings

    for pattern, label in SENSITIVE_PATTERNS:
        matches = re.finditer(pattern, content)
        for m in matches:
            line_num = content[:m.start()].count('\n') + 1
            findings.append({
                "type": label,
                "file": os.path.relpath(filepath, WORKSPACE),
                "line": line_num,
                "match_preview": m.group()[:30] + "..." if len(m.group()) > 30 else m.group(),
            })
    return findings


def audit_soul_md() -> dict:
    """审计 SOUL.md 的安全配置完整性。"""
    result = {"exists": False, "checks": [], "score": 0, "total": len(SOUL_CHECKLIST)}
    soul_path = os.path.join(WORKSPACE, "SOUL.md")

    if not os.path.exists(soul_path):
        return result

    result["exists"] = True
    with open(soul_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read().lower()

    for check_name, patterns in SOUL_CHECKLIST:
        found = any(re.search(p, content, re.IGNORECASE) for p in patterns)
        result["checks"].append({"name": check_name, "pass": found})
        if found:
            result["score"] += 1

    return result


def audit_agents_md() -> dict:
    """审计 AGENTS.md 的安全配置。"""
    result = {"exists": False, "checks": [], "score": 0, "total": len(AGENTS_CHECKLIST)}
    agents_path = os.path.join(WORKSPACE, "AGENTS.md")

    if not os.path.exists(agents_path):
        return result

    result["exists"] = True
    with open(agents_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read().lower()

    for check_name, patterns in AGENTS_CHECKLIST:
        found = any(re.search(p, content, re.IGNORECASE) for p in patterns)
        result["checks"].append({"name": check_name, "pass": found})
        if found:
            result["score"] += 1

    return result


def check_unexpected_files() -> list:
    """检查 workspace 中是否有意外的可执行文件或脚本。"""
    suspicious = []
    exec_extensions = {'.sh', '.bash', '.py', '.rb', '.pl', '.js', '.ts', '.exe', '.bin', '.app'}

    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        rel_root = os.path.relpath(root, WORKSPACE)

        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, WORKSPACE)
            ext = Path(fname).suffix.lower()

            # 检查可执行权限
            if os.access(fpath, os.X_OK) and ext not in {'.md', '.txt', ''}:
                suspicious.append({
                    "file": rel_path,
                    "reason": "可执行权限",
                })

            # 检查可执行扩展名（在非 memory/ 非 skill 相关目录）
            if ext in exec_extensions and not rel_root.startswith('memory'):
                suspicious.append({
                    "file": rel_path,
                    "reason": f"可执行文件扩展名 ({ext})",
                })

    return suspicious


def check_file_permissions() -> dict:
    """检查 workspace 目录权限。"""
    result = {}
    ws_stat = os.stat(WORKSPACE)
    mode = oct(ws_stat.st_mode)[-3:]
    result["workspace_mode"] = mode
    result["workspace_ok"] = mode in ("755", "750", "700")

    # 检查关键文件
    for fname in ["SOUL.md", "MEMORY.md", "USER.md", "IDENTITY.md"]:
        fpath = os.path.join(WORKSPACE, fname)
        if os.path.exists(fpath):
            fstat = os.stat(fpath)
            fmode = oct(fstat.st_mode)[-3:]
            result[fname] = {"mode": fmode, "ok": int(fmode[1]) <= 4 and int(fmode[2]) <= 4}

    return result


def main():
    report = {
        "audit_time": datetime.now().isoformat(),
        "workspace": WORKSPACE,
        "soul_audit": audit_soul_md(),
        "agents_audit": audit_agents_md(),
        "secrets_found": [],
        "unexpected_files": check_unexpected_files(),
        "file_permissions": check_file_permissions(),
    }

    # 扫描所有 md 文件中的明文敏感信息
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in files:
            if fname.endswith('.md'):
                fpath = os.path.join(root, fname)
                secrets = check_file_for_secrets(fpath)
                report["secrets_found"].extend(secrets)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
