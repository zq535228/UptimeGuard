#!/usr/bin/env python3
"""
status_check.py

检查 UptimeGuard 应用状态和 Telegram 功能。
"""

import os
import sys
import time
from telegram_config import load_config, is_telegram_configured
from monitor import latest_status_snapshot


def check_application_status():
    """检查应用状态"""
    print("🔍 UptimeGuard 应用状态检查")
    print("=" * 50)
    
    # 检查日志文件
    log_file = "logs/uptime.log"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"✅ 日志文件存在，共 {len(lines)} 行记录")
        
        # 显示最新几条日志
        print("\n📝 最新日志记录:")
        for line in lines[-3:]:
            print(f"   {line.strip()}")
    else:
        print("❌ 日志文件不存在")
    
    print()
    
    # 检查状态快照
    print("📊 当前监控状态:")
    if latest_status_snapshot:
        for url, status in latest_status_snapshot.items():
            name = status.get('name', 'Unknown')
            status_text = status.get('status', 'Unknown')
            failures = status.get('consecutive_failures', 0)
            latency = status.get('latency_ms', 0)
            print(f"   {name}: {status_text} (失败: {failures}, 延迟: {latency}ms)")
    else:
        print("   ⚠️ 暂无监控数据")
    
    print()
    
    # 检查 Telegram 配置
    print("🔔 Telegram 配置状态:")
    config = load_config()
    print(f"   启用状态: {'✅ 已启用' if config['enabled'] else '❌ 未启用'}")
    print(f"   Bot Token: {'✅ 已配置' if config['bot_token'] else '❌ 未配置'}")
    print(f"   Chat ID: {'✅ 已配置' if config['chat_id'] else '❌ 未配置'}")
    print(f"   失败阈值: {config['failure_threshold']} 次")
    print(f"   配置完整: {'✅ 是' if is_telegram_configured() else '❌ 否'}")
    
    print()
    
    # 检查配置文件
    print("📁 配置文件状态:")
    files_to_check = [
        "sites.json",
        "logs/uptime.log"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} (不存在)")
    
    print()
    
    # 总结
    print("📋 状态总结:")
    if is_telegram_configured():
        print("   🎉 所有功能正常，Telegram 通知已就绪！")
    else:
        print("   ⚠️  Telegram 未配置，但监控功能正常")
    
    print("   💡 访问 http://127.0.0.1:7860 查看 Web 界面")


if __name__ == "__main__":
    check_application_status()
