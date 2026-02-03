#!/usr/bin/env python3
"""
实时聊天记录保存模块

在对话结束时调用此脚本，自动保存最近的消息

Usage:
    # 在对话结束时自动保存
    python3 realtime_save.py --session "agent:main:main" --limit 10
"""

import sqlite3
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from init_db import DB_PATH, init_db

def should_save_message(content_parts):
    """判断是否应该保存这条消息"""
    for part in content_parts:
        if isinstance(part, dict) and part.get("type") == "text":
            text = part.get("text", "")
            # 排除系统消息和太短的回复
            if len(text) > 10 and not text.startswith("System:"):
                return True
    return False

def extract_text_content(content_parts):
    """提取文本内容"""
    text_parts = []
    for part in content_parts:
        if isinstance(part, dict) and part.get("type") == "text":
            text_parts.append(part.get("text", ""))
    return "\n".join(text_parts)

def save_single_message(session_key, session_name, msg):
    """保存单条消息到数据库"""
    if not DB_PATH.exists():
        init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查是否已存在（避免重复保存）
    timestamp = msg.get("timestamp", 0)
    content = extract_text_content(msg.get("content", []))
    
    if not content.strip():
        conn.close()
        return False
    
    cursor.execute('''
        SELECT 1 FROM messages 
        WHERE session_key = ? AND timestamp = ? AND content = ?
    ''', (session_key, timestamp, content))
    
    if cursor.fetchone():
        conn.close()
        return False  # 已存在，跳过
    
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
        msg.get("author", ""),
        content,
        msg.get("messageId", "")
    ))
    
    conn.commit()
    conn.close()
    return True

def main():
    parser = argparse.ArgumentParser(description="实时保存单条消息")
    parser.add_argument("--session-key", required=True, help="会话 key")
    parser.add_argument("--session-name", default="Unknown", help="会话名称")
    parser.add_argument("--message-file", help="JSON 格式的消息文件")
    args = parser.parse_args()
    
    if args.message_file:
        with open(args.message_file, 'r') as f:
            msg = json.load(f)
        if save_single_message(args.session_key, args.session_name, msg):
            print("✅ 消息已保存")
        else:
            print("⏭️ 消息已存在或无需保存")
    else:
        print("📌 使用说明:")
        print("  此脚本用于保存单条消息，通常由 Agent 自动调用")
        print("  参数: --session-key, --session-name, --message-file")

if __name__ == "__main__":
    main()
