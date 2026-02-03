#!/usr/bin/env python3
"""
查看聊天记录存档统计

Usage:
    python3 stats.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from init_db import DB_PATH

def get_stats():
    """获取统计信息"""
    if not DB_PATH.exists():
        print(f"❌ 数据库不存在: {DB_PATH}")
        print("请先运行: python3 init_db.py")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总消息数
    cursor.execute('SELECT COUNT(*) FROM messages')
    total = cursor.fetchone()[0]
    
    # 会话数
    cursor.execute('SELECT COUNT(DISTINCT session_key) FROM messages')
    sessions = cursor.fetchone()[0]
    
    # 最早和最晚的消息
    cursor.execute('SELECT MIN(datetime), MAX(datetime) FROM messages')
    earliest, latest = cursor.fetchone()
    
    # 今日消息
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(*) FROM messages WHERE datetime LIKE ?', (f'{today}%',))
    today_count = cursor.fetchone()[0]
    
    # 角色统计
    cursor.execute('''
        SELECT role, COUNT(*) FROM messages 
        GROUP BY role 
        ORDER BY COUNT(*) DESC
    ''')
    role_stats = cursor.fetchall()
    
    # 会话列表
    cursor.execute('''
        SELECT session_name, COUNT(*) as cnt 
        FROM messages 
        GROUP BY session_key, session_name
        ORDER BY cnt DESC
        LIMIT 10
    ''')
    top_sessions = cursor.fetchall()
    
    conn.close()
    
    # 打印统计
    print("=" * 60)
    print("📊 聊天记录存档统计")
    print("=" * 60)
    print(f"\n💾 数据库: {DB_PATH}")
    print(f"\n📈 总体统计:")
    print(f"   总消息数: {total:,}")
    print(f"   会话数量: {sessions}")
    print(f"   今日消息: {today_count}")
    if earliest and latest:
        print(f"   时间范围: {earliest} ~ {latest}")
    
    print(f"\n👤 角色分布:")
    for role, count in role_stats:
        print(f"   {role}: {count:,}")
    
    print(f"\n🏆 消息最多的会话:")
    for name, count in top_sessions:
        name = name or "Unknown"
        print(f"   {name}: {count:,}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    get_stats()
