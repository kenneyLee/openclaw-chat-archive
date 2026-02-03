#!/usr/bin/env python3
"""
Internal: Save session history messages to database
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from init_db import DB_PATH

def save_session_messages(session_key, session_name, messages):
    """Save messages to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    count = 0
    for msg in messages:
        timestamp = msg.get("timestamp", 0)
        if not timestamp:
            continue
            
        dt = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract text content
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

if __name__ == "__main__":
    # Session data from sessions_history
    session_key = "agent:main:main"
    session_name = "Joe Root"
    
    # Message data (passed from the tool result)
    messages_data = '''[
  {
    "role": "assistant",
    "content": [{"type": "text", "text": "我来查看现有的 `chat-history` skill，然后帮你实现聊天记录保存和搜索功能。"}],
    "timestamp": 1770128459666
  },
  {
    "role": "user", 
    "content": [{"type": "text", "text": "以下是音訊內容的逐字稿： 「好的，那我現在要你實現一個 skill，就是保存我們的、存儲我們的聊天記錄，然後支持搜索。」"}],
    "timestamp": 1770128459664
  }
]'''
    
    messages = json.loads(messages_data)
    count = save_session_messages(session_key, session_name, messages)
    print(f"✅ 已保存 {count} 条消息")
