#!/usr/bin/env python3
"""
搜索聊天记录

Usage:
    python3 search_chat.py "关键词"           # 搜索包含关键词的消息
    python3 search_chat.py "API设计" --days 7  # 搜索最近7天
    python3 search_chat.py "数据库" --limit 20 # 显示前20条结果
    python3 search_chat.py "会议" --export results.md
"""

import argparse
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from init_db import DB_PATH

def search_messages(
    keyword: str,
    days: int = None,
    session_key: str = None,
    limit: int = 50
):
    """搜索消息"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''
        SELECT * FROM messages 
        WHERE content LIKE ?
    '''
    params = [f'%{keyword}%']
    
    if days:
        since = datetime.now() - timedelta(days=days)
        timestamp = int(since.timestamp() * 1000)
        query += ' AND timestamp > ?'
        params.append(timestamp)
    
    if session_key:
        query += ' AND session_key = ?'
        params.append(session_key)
    
    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results

def format_result(msg: dict, index: int) -> str:
    """格式化搜索结果"""
    return f"""
[{index}] {msg['datetime']} | {msg.get('session_name', 'Unknown')}
    {msg['role']}: {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}
"""

def export_to_markdown(results: list, filepath: str):
    """导出为 Markdown"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 聊天记录搜索结果\n\n")
        f.write(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"共找到 {len(results)} 条结果\n\n")
        f.write("---\n\n")
        
        for i, msg in enumerate(results, 1):
            f.write(f"## [{i}] {msg['datetime']}\n\n")
            f.write(f"**会话:** {msg.get('session_name', 'Unknown')}\n\n")
            f.write(f"**角色:** {msg['role']}\n\n")
            f.write(f"**内容:**\n\n{msg['content']}\n\n")
            f.write("---\n\n")
    
    print(f"✅ 已导出到: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="搜索聊天记录")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--days", type=int, help="搜索最近 N 天")
    parser.add_argument("--session", type=str, help="指定会话")
    parser.add_argument("--limit", type=int, default=50, help="结果数量限制")
    parser.add_argument("--export", type=str, help="导出到文件 (.md)")
    args = parser.parse_args()
    
    if not DB_PATH.exists():
        print(f"❌ 数据库不存在: {DB_PATH}")
        print("请先运行: python3 init_db.py")
        return 1
    
    print(f"🔍 搜索: '{args.keyword}'")
    if args.days:
        print(f"📅 时间范围: 最近 {args.days} 天")
    
    results = search_messages(
        keyword=args.keyword,
        days=args.days,
        session_key=args.session,
        limit=args.limit
    )
    
    print(f"\n✅ 找到 {len(results)} 条结果\n")
    
    if not results:
        print("没有找到匹配的消息。")
        return 0
    
    # 显示结果
    for i, msg in enumerate(results[:20], 1):  # 最多显示20条
        print(format_result(msg, i))
    
    if len(results) > 20:
        print(f"... 还有 {len(results) - 20} 条结果 ...")
    
    # 导出
    if args.export:
        export_to_markdown(results, args.export)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
