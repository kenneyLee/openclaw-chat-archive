#!/usr/bin/env python3
"""
保存聊天记录到本地数据库

Usage:
    python3 save_chat.py                    # 保存最近50条
    python3 save_chat.py --limit 200        # 保存最近200条
    python3 save_chat.py --session KEY      # 保存指定会话
    python3 save_chat.py --all              # 保存所有会话
"""

import argparse
import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from init_db import DB_PATH, init_db

# 尝试导入 OpenClaw 工具
# 注意：实际运行时由 agent 调用 sessions_list/sessions_history
def save_messages(session_key: str, session_name: str, messages: list):
    """保存消息到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    count = 0
    for msg in messages:
        timestamp = msg.get("timestamp", 0)
        dt = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
        
        # 提取内容
        content_parts = msg.get("content", [])
        text_parts = []
        for part in content_parts:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
        content = "\n".join(text_parts) if text_parts else ""
        
        if not content.strip():
            continue
        
        cursor.execute('''
            INSERT OR IGNORE INTO messages 
            (session_key, session_name, timestamp, datetime, role, author, content, message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_key,
            session_name,
            timestamp,
            dt,
            msg.get("role", "unknown"),
            msg.get("author", ""),
            content,
            msg.get("messageId", "")
        ))
        count += 1
    
    conn.commit()
    conn.close()
    return count

def main():
    parser = argparse.ArgumentParser(description="保存聊天记录")
    parser.add_argument("--limit", type=int, default=50, help="消息数量限制")
    parser.add_argument("--session", type=str, help="指定会话 key")
    parser.add_argument("--all", action="store_true", help="保存所有会话")
    args = parser.parse_args()
    
    # 确保数据库存在
    if not DB_PATH.exists():
        init_db()
    
    print(f"📥 准备保存最近 {args.limit} 条消息...")
    print(f"💾 数据库位置: {DB_PATH}")
    
    # 这里显示调用说明，实际由 agent 调用 OpenClaw 工具
    print("""
📌 使用说明:

此脚本需要配合 OpenClaw agent 使用。

请向 agent 发送以下指令:

1. 保存当前会话:
   "保存我们最近的聊天记录"

2. 保存指定会话:
   "保存会话 agent:main:telegram:group:-123456789 的聊天记录"

3. 保存多个会话:
   "保存所有会话的聊天记录"

Agent 将调用以下工具:
   • sessions_list - 获取会话列表
   • sessions_history - 获取消息历史
   
然后保存到: {DB_PATH}
""")

if __name__ == "__main__":
    main()
