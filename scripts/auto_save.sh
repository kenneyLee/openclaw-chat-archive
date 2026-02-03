#!/bin/bash
# Auto-save chat history every 30 minutes
# Add to crontab: */30 * * * * /home/wshi3788/clawd/skills/chat-archive/scripts/auto_save.sh

cd /home/wshi3788/clawd/skills/chat-archive

# Save recent messages from all active sessions
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/wshi3788/clawd/skills/chat-archive/scripts')
from init_db import DB_PATH
import sqlite3
from datetime import datetime

# Note: This requires agent interaction to call sessions_list/sessions_history
# For now, just log that auto-save was attempted
with open('/home/wshi3788/clawd/skills/chat-archive/data/auto_save.log', 'a') as f:
    f.write(f"[{datetime.now()}] Auto-save triggered\n")

print("⏰ 定时保存触发 - 请手动执行保存或使用 agent 调用")
EOF
