#!/usr/bin/env python3
"""
Skill Guardian - 已安装 Skill 批量扫描脚本
扫描 ~/.openclaw/skills/ 下所有 skill，检查红线模式匹配。
输出 JSON 报告供 Agent 解读。
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime

# 红线模式（正则）
RED_FLAG_PATTERNS = {
    "A_network_external": {
        "label": "网络/数据外传",
        "patterns": [
            r'\bcurl\b', r'\bwget\b', r'\bfetch\s*\(', r'\brequests\.',
            r'\bhttp\.client\b', r'\burllib\b', r'\baxios\b', r'\bnode-fetch\b',
            r'\bXMLHttpRequest\b', r'\bWebSocket\b', r'\bsocket\.connect\b',
            r'\bnet\.connect\b',
        ]
    },
    "A_ip_address": {
        "label": "IP 地址直连（可疑）",
        "patterns": [
            r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
        ]
    },
    "B_credentials": {
        "label": "凭证/敏感信息访问",
        "patterns": [
            r'API_KEY', r'SECRET', r'TOKEN', r'PASSWORD', r'CREDENTIAL',
            r'\.ssh[/\\]', r'\.aws[/\\]', r'\.config/gh', r'\.gnupg[/\\]',
            r'\.pem\b', r'\.p12\b', r'keychain', r'credential\.store',
            r'password-store',
        ]
    },
    "B_env_secrets": {
        "label": "环境变量读取（可能含密钥）",
        "patterns": [
            r'os\.environ', r'process\.env',
        ]
    },
    "C_memory_files": {
        "label": "Agent 记忆文件访问",
        "patterns": [
            r'MEMORY\.md', r'USER\.md', r'SOUL\.md', r'IDENTITY\.md',
            r'AGENTS\.md', r'HEARTBEAT\.md', r'BOOTSTRAP\.md',
            r'\.openclaw/',
        ]
    },
    "D_code_execution": {
        "label": "动态代码执行",
        "patterns": [
            r'\beval\s*\(', r'\bexec\s*\(', r'\bexecSync\b', r'\bspawn\s*\(',
            r'\bchild_process\b', r'\bsubprocess\b', r'\bos\.system\b',
            r'\bos\.popen\b', r'__import__',
        ]
    },
    "D_obfuscation": {
        "label": "代码混淆/编码执行",
        "patterns": [
            r'base64\.b64decode', r'\batob\s*\(', r'Buffer\.from.*base64',
            r'\bcompile\s*\(',
        ]
    },
    "E_system_privilege": {
        "label": "系统权限操作",
        "patterns": [
            r'\bsudo\b', r'\bsu\s+-', r'\bchmod\b', r'\bchown\b',
            r'/etc/', r'/usr/', r'crontab', r'launchd', r'systemctl',
            r'\.bashrc', r'\.zshrc', r'\.profile',
            r'\bapt\s+install', r'\bbrew\s+install', r'\bpip\s+install',
            r'\bnpm\s+install\s+-g',
        ]
    },
    "F_stealth": {
        "label": "隐蔽/后台行为",
        "patterns": [
            r'\bnohup\b', r'\bdisown\b', r'\bdaemon\b',
            r'telemetry', r'analytics', r'tracking', r'beacon',
            r'phone\.home',
        ]
    },
}

SKIP_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico',
                   '.pdf', '.zip', '.tar', '.gz', '.skill',
                   '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.mp4'}


def scan_file(filepath: str) -> list:
    """扫描单个文件，返回匹配的红线项。"""
    hits = []
    ext = Path(filepath).suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return hits

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except (IOError, OSError):
        return hits

    for category, info in RED_FLAG_PATTERNS.items():
        for pattern in info['patterns']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for m in matches:
                # 找到匹配所在行
                line_start = content.rfind('\n', 0, m.start()) + 1
                line_end = content.find('\n', m.end())
                if line_end == -1:
                    line_end = len(content)
                line = content[line_start:line_end].strip()
                line_num = content[:m.start()].count('\n') + 1

                hits.append({
                    "category": category,
                    "label": info['label'],
                    "pattern": pattern,
                    "match": m.group(),
                    "line": line_num,
                    "context": line[:200],
                })
    return hits


def scan_skill(skill_path: str) -> dict:
    """扫描一个 skill 目录，返回扫描结果。"""
    skill_name = os.path.basename(skill_path)
    result = {
        "name": skill_name,
        "path": skill_path,
        "files_scanned": 0,
        "total_hits": 0,
        "hits_by_category": {},
        "details": [],
    }

    for root, dirs, files in os.walk(skill_path):
        # 跳过隐藏目录和 node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for fname in files:
            if fname.startswith('.'):
                continue
            fpath = os.path.join(root, fname)
            result["files_scanned"] += 1
            hits = scan_file(fpath)
            if hits:
                rel_path = os.path.relpath(fpath, skill_path)
                for h in hits:
                    h["file"] = rel_path
                    cat = h["category"]
                    result["hits_by_category"][cat] = result["hits_by_category"].get(cat, 0) + 1
                result["details"].extend(hits)
                result["total_hits"] += len(hits)

    return result


def classify_risk(scan_result: dict) -> str:
    """根据扫描结果判定风险等级。"""
    cats = set(scan_result["hits_by_category"].keys())
    total = scan_result["total_hits"]

    # 极端风险
    extreme_cats = {"D_obfuscation", "A_ip_address"}
    if cats & extreme_cats:
        return "⛔ EXTREME"

    # 高风险
    high_cats = {"B_credentials", "C_memory_files", "E_system_privilege", "D_code_execution"}
    if cats & high_cats:
        return "🔴 HIGH"

    # 中风险
    medium_cats = {"A_network_external", "B_env_secrets", "F_stealth"}
    if cats & medium_cats:
        return "🟡 MEDIUM"

    if total == 0:
        return "🟢 LOW"

    return "🟢 LOW"


def main():
    skills_dir = os.path.expanduser("~/.openclaw/skills")
    # 自身目录名，扫描时跳过（安全审查 skill 自身会命中大量红线关键词）
    SELF_SKILL_NAME = "skill-guardian"

    if len(sys.argv) > 1:
        # 扫描指定 skill
        target = sys.argv[1]
        if os.path.isdir(target):
            skill_path = target
        else:
            skill_path = os.path.join(skills_dir, target)

        if not os.path.isdir(skill_path):
            print(json.dumps({"error": f"Skill not found: {skill_path}"}))
            sys.exit(1)

        result = scan_skill(skill_path)
        result["risk_level"] = classify_risk(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 扫描所有已装 skill
        if not os.path.isdir(skills_dir):
            print(json.dumps({"error": f"Skills directory not found: {skills_dir}"}))
            sys.exit(1)

        report = {
            "scan_time": datetime.now().isoformat(),
            "skills_dir": skills_dir,
            "total_skills": 0,
            "results": [],
        }

        for entry in sorted(os.listdir(skills_dir)):
            entry_path = os.path.join(skills_dir, entry)
            if os.path.isdir(entry_path) and not entry.startswith('.') and entry != SELF_SKILL_NAME:
                result = scan_skill(entry_path)
                result["risk_level"] = classify_risk(result)
                report["results"].append(result)
                report["total_skills"] += 1

        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
