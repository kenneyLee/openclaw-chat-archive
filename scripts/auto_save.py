#!/usr/bin/env python3
"""
自动保存聊天记录 - 供定时任务调用

Usage:
    python3 auto_save.py --session-key "agent:main:main" --limit 50
"""

import sqlite3
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
from init_db import DB_PATH, init_db


def get_last_saved_timestamp(session_key):
    """获取某个会话最后一次保存的消息时间戳"""
    if not DB_PATH.exists():
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(timestamp) FROM messages 
        WHERE session_key = ?
    ''', (session_key,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] else 0


def save_messages_batch(session_key, session_name, messages):
    """批量保存消息，自动去重"""
    if not messages:
        return 0
    
    if not DB_PATH.exists():
        init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    saved_count = 0
    
    for msg in messages:
        # 提取文本内容
        content_parts = msg.get("content", [])
        text_parts = []
        for part in content_parts:
            if isinstance(part, dict) and part.get("type") == "text":
                text = part.get("text", "").strip()
                if text:
                    text_parts.append(text)
        
        content = "\n".join(text_parts).strip()
        if not content:
            continue
            
        # 排除系统消息和太短的回复
        if len(content) < 10 or content.startswith("System:"):
            continue
        
        timestamp = msg.get("timestamp", 0)
        
        # 检查是否已存在
        cursor.execute('''
            SELECT 1 FROM messages 
            WHERE session_key = ? AND timestamp = ? AND content = ?
        ''', (session_key, timestamp, content))
        
        if cursor.fetchone():
            continue  # 已存在，跳过
        
        # 插入新消息
        dt = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO messages 
            (session_key, session_name, timestamp, datetime, role, author, content, message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_key,
            session_name,
            timestamp,
            dt,
            msg.get("role", "unknown"),
            msg.get("author", "system"),
            content,
            msg.get("messageId", "")
        ))
        saved_count += 1
    
    conn.commit()
    conn.close()
    return saved_count


def main():
    parser = argparse.ArgumentParser(description="自动保存聊天记录")
    parser.add_argument("--session-key", default="agent:main:main", help="会话 key")
    parser.add_argument("--session-name", default="Main", help="会话名称")
    parser.add_argument("--limit", type=int, default=100, help="获取最近多少条消息")
    args = parser.parse_args()
    
    # 获取上次保存的时间戳
    last_timestamp = get_last_saved_timestamp(args.session_key)
    
    # 输出状态（用于日志）
    print(f"📁 数据库: {DB_PATH}")
    print(f"💬 会话: {args.session_key}")
    print(f"⏰ 上次保存: {datetime.fromtimestamp(last_timestamp/1000) if last_timestamp else '无'}")
    print(f"📊 获取最近 {args.limit} 条消息...")
    
    # 注意：实际的消息获取需要由调用方（Agent）提供
    # 这个脚本只负责保存传入的消息数据
    print("\n💡 提示: 此脚本需要配合 Agent 的 sessions_history API 使用")
    print("   Agent 获取历史消息后，调用此脚本保存到数据库")


if __name__ == "__main__":
    main()
