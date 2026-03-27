# 红线检查详细参考

本文档包含每条红线规则的具体代码模式，供审查时 grep/搜索使用。

## A. 网络与数据外传

### 搜索模式
```
curl | wget | fetch( | requests\. | http\.client | urllib
axios | got( | node-fetch | XMLHttpRequest
WebSocket | socket\.connect | net\.connect
```

### 判断标准
- 目标是否为 skill 声明功能所必需的已知服务？
- 目标是域名还是纯 IP？（纯 IP 高度可疑）
- 是否发送了本地数据（尤其是文件内容、环境变量）？
- 是否有硬编码的陌生 URL？

## B. 凭证与敏感信息

### 搜索模式
```
API_KEY | SECRET | TOKEN | PASSWORD | CREDENTIAL
\.ssh | \.aws | \.config/gh | \.gnupg
\.pem | \.p12 | \.key | \.cert
keychain | credential.store | password-store
os\.environ | process\.env
```

### 判断标准
- 读取凭证是否为其核心功能所必需？（如 AWS skill 读 ~/.aws 可以接受）
- 是否将读取到的凭证发送到外部？
- 是否将凭证写入日志或非安全位置？

## C. Agent 记忆文件

### 搜索模式
```
MEMORY\.md | USER\.md | SOUL\.md | IDENTITY\.md
AGENTS\.md | HEARTBEAT\.md | BOOTSTRAP\.md
memory/ | \.openclaw/
workspace/MEMORY | workspace/USER | workspace/SOUL
```

### 判断标准
- 一个正常的功能性 skill 几乎没有理由读取这些文件
- 唯一合理例外：安全审计类 skill（如本 skill）以只读方式检查配置
- 如果读取后将内容发送到外部 → ⛔ 立即拒绝

## D. 代码执行与混淆

### 搜索模式
```
eval( | exec( | execSync | spawn( | child_process
subprocess | os\.system | os\.popen
base64\.b64decode | atob( | Buffer\.from.*base64
compile( | __import__
```

### 混淆特征
- 大段无法阅读的字符串（base64、hex、unicode escape）
- 变量名全是单字母或随机字符
- 字符串拼接构建命令（`cmd = "rm" + " -rf" + " /"`)
- 压缩/混淆的 JS（单行超长代码）

## E. 系统权限

### 搜索模式
```
sudo | su - | chmod | chown | chgrp
/etc/ | /usr/ | /var/ | /System/
crontab | launchd | systemd | systemctl
\.bashrc | \.zshrc | \.profile | \.bash_profile
apt | brew | yum | pip install | npm install -g
```

### 判断标准
- 安装依赖是否在文档中明确声明？
- 修改系统配置是否为核心功能所必需？
- 是否请求了超出必要范围的权限？

## F. 隐蔽行为

### 搜索模式
```
background | daemon | nohup | disown | &$
setInterval | setTimeout.*[0-9]{4,} | cron
telemetry | analytics | tracking | beacon
phone.home | heartbeat.*http | ping.*http
```

### 判断标准
- 后台进程是否在文档中声明？
- 定时任务的用途是否透明？
- 是否有未声明的网络通信（遥测/心跳/统计）？
