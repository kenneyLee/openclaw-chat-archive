#!/usr/bin/env python3
"""
导出聊天记录

Usage:
    python3 export_chat.py                    # 导出最近50条
    python3 export_chat.py --days 7           # 导出最近7天
    python3 export_chat.py --output chat.md   # 指定输出文件
    python3 export_chat.py --session KEY      # 导出指定会话
    python3 export_chat.py --format json      # JSON格式
"""

import argparse
import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from init_db import DB_PATH

def export_messages(
    output_path: str,
    days: int = None,
    session_key: str = None,
    limit: int = 500,
    format_type: str = "markdown"
):
    """导出消息"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM messages WHERE 1=1'
    params = []
    
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
    
    # 按时间正序排列
    results.reverse()
    
    if format_type == "json":
        export_json(results, output_path)
    else:
        export_markdown(results, output_path)
    
    return len(results)

def export_markdown(results: list, filepath: str):
    """导出为 Markdown"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 聊天记录归档\n\n")
        f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"消息数量: {len(results)}\n\n")
        f.write("---\n\n")
        
        current_date = None
        for msg in results:
            msg_date = msg['datetime'][:10]  # YYYY-MM-DD
            
            if msg_date != current_date:
                current_date = msg_date
                f.write(f"## 📅 {current_date}\n\n")
            
            time = msg['datetime'][11:16]  # HH:MM
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            
            f.write(f"**{time}** {role_icon} **{msg['role']}**:\n\n")
            f.write(f"{msg['content']}\n\n")
            f.write("---\n\n")

def export_json(results: list, filepath: str):
    """导出为 JSON"""
    data = {
        "export_time": datetime.now().isoformat(),
        "count": len(results),
        "messages": results
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description="导出聊天记录")
    parser.add_argument("--output", type=str, default="chat_export.md", help="输出文件")
    parser.add_argument("--days", type=int, help="导出最近 N 天")
    parser.add_argument("--session", type=str, help="指定会话")
    parser.add_argument("--limit", type=int, default=500, help="消息数量限制")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="格式")
    args = parser.parse_args()
    
    if not DB_PATH.exists():
        print(f"❌ 数据库不存在: {DB_PATH}")
        print("请先运行: python3 init_db.py")
        return 1
    
    print(f"📤 导出聊天记录...")
    if args.days:
        print(f"📅 时间范围: 最近 {args.days} 天")
    print(f"💾 输出文件: {args.output}")
    
    count = export_messages(
        output_path=args.output,
        days=args.days,
        session_key=args.session,
        limit=args.limit,
        format_type=args.format
    )
    
    print(f"✅ 成功导出 {count} 条消息")
    return 0

if __name__ == "__main__":
    sys.exit(main())
