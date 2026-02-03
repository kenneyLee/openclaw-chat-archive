#!/usr/bin/env python3
"""
Chat Archive - 聊天记录自动保存与搜索工具

功能：
1. 自动保存聊天记录到本地 SQLite 数据库
2. 支持关键词搜索
3. 支持按时间范围查询
4. 支持导出到 Markdown 或 JSON

Usage:
    # 保存当前会话的消息
    python3 save_chat.py --limit 100
    
    # 搜索关键词
    python3 search_chat.py "数据库设计" --days 7
    
    # 导出到文件
    python3 export_chat.py --output backup.md --days 30
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 数据存储路径
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "chat_archive.db"

def init_db():
    """初始化数据库"""
    DATA_DIR.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_key TEXT NOT NULL,
            session_name TEXT,
            timestamp INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            role TEXT NOT NULL,
            author TEXT,
            content TEXT NOT NULL,
            message_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON messages(session_key)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_content ON messages(content)')
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DB_PATH}")

if __name__ == "__main__":
    init_db()
