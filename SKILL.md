---
name: chat-archive
description: Save and search chat history from Telegram groups and sessions. Automatically archive messages to local SQLite database with full-text search support.
---

# Chat Archive - 聊天记录存档与搜索

## 功能概述

自动保存聊天记录到本地 SQLite 数据库，支持关键词搜索、时间范围筛选和导出功能。

## 安装与初始化

```bash
# 1. 进入 skill 目录
cd /home/wshi3788/clawd/skills/chat-archive

# 2. 初始化数据库
python3 scripts/init_db.py
```

## 使用方法

### 1. 保存聊天记录

向 Agent 发送指令：

```
保存我们最近的聊天记录
```

Agent 会调用 `sessions_history` 工具获取消息，并保存到本地数据库。

### 2. 搜索聊天记录

```bash
# 搜索关键词
python3 scripts/search_chat.py "数据库设计"

# 搜索最近7天
python3 scripts/search_chat.py "API" --days 7

# 导出搜索结果
python3 scripts/search_chat.py "会议" --export results.md
```

### 3. 导出聊天记录

```bash
# 导出为 Markdown
python3 scripts/export_chat.py --output backup.md --days 30

# 导出为 JSON
python3 scripts/export_chat.py --format json --output backup.json

# 导出所有消息
python3 scripts/export_chat.py --limit 1000
```

### 4. 查看统计

```bash
# 查看存档统计
python3 scripts/stats.py
```

## 数据存储

- **数据库位置**: `skills/chat-archive/data/chat_archive.db`
- **表结构**: `messages` 表存储所有消息
- **索引**: 支持按会话、时间、内容搜索

## 常用场景

### 场景1：保存重要讨论
```
"保存今天关于需求讨论的聊天记录"
```

### 场景2：查找之前的决定
```bash
python3 scripts/search_chat.py "决定" --days 30
```

### 场景3：导出会议记录
```bash
python3 scripts/export_chat.py --days 1 --output meeting_2026-02-03.md
```

### 场景4：搜索代码片段
```bash
python3 scripts/search_chat.py "```python" --limit 10
```

## API 参考

### 数据库表结构

```sql
messages:
  - id: INTEGER PRIMARY KEY
  - session_key: TEXT (会话标识)
  - session_name: TEXT (会话名称)
  - timestamp: INTEGER (时间戳毫秒)
  - datetime: TEXT (可读时间)
  - role: TEXT (user/assistant)
  - author: TEXT (作者)
  - content: TEXT (消息内容)
  - message_id: TEXT (消息ID)
  - created_at: TIMESTAMP (存档时间)
```

### 脚本参数

**search_chat.py**
- `keyword`: 搜索关键词（必填）
- `--days`: 搜索最近 N 天
- `--session`: 指定会话 key
- `--limit`: 结果数量限制（默认50）
- `--export`: 导出到文件

**export_chat.py**
- `--output`: 输出文件路径
- `--days`: 导出最近 N 天
- `--session`: 指定会话
- `--limit`: 消息数量限制（默认500）
- `--format`: 格式 (markdown/json)

## 注意事项

1. 数据库文件存储在本地，定期备份重要数据
2. 搜索使用 SQLite LIKE 匹配，支持模糊搜索
3. 导出大量消息时可能需要较长时间
4. 可以通过 cron 定时任务自动备份

## 自动化备份示例

```bash
# 每天凌晨备份昨天的聊天记录
0 2 * * * cd /home/wshi3788/clawd/skills/chat-archive && python3 scripts/save_chat.py --limit 1000
```
