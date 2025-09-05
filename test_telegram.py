#!/usr/bin/env python3
"""
test_telegram.py

Telegram 通知功能测试脚本。
用于测试 Telegram 配置和通知发送功能。
"""

import os
import sys
import time
from telegram_config import load_config, update_config, is_telegram_configured
from telegram_notifier import test_telegram_connection, send_site_down_alert, send_site_recovery_alert


def main():
    """主测试函数"""
    print("🧪 UptimeGuard Telegram 通知测试")
    print("=" * 50)
    
    # 检查当前配置
    config = load_config()
    print(f"当前配置状态: {config}")
    print(f"配置是否完整: {is_telegram_configured()}")
    print()
    
    if not is_telegram_configured():
        print("❌ Telegram 未配置，请先在 UI 中配置或设置环境变量")
        print("\n环境变量示例:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("export TELEGRAM_CHAT_ID='your_chat_id'")
        print("export TELEGRAM_ENABLED='true'")
        print("export TELEGRAM_FAILURE_THRESHOLD='10'")
        return
    
    # 测试连接
    print("🔗 测试 Telegram 连接...")
    if test_telegram_connection():
        print("✅ 连接测试成功！")
    else:
        print("❌ 连接测试失败！")
        return
    
    print()
    
    # 测试故障警报
    print("🚨 测试故障警报...")
    if send_site_down_alert(
        site_name="测试网站",
        site_url="https://example.com",
        consecutive_failures=10,
        error_info="连接超时"
    ):
        print("✅ 故障警报发送成功！")
    else:
        print("❌ 故障警报发送失败！")
    
    time.sleep(2)
    
    # 测试恢复通知
    print("✅ 测试恢复通知...")
    if send_site_recovery_alert(
        site_name="测试网站",
        site_url="https://example.com",
        latency_ms=150
    ):
        print("✅ 恢复通知发送成功！")
    else:
        print("❌ 恢复通知发送失败！")
    
    print()
    print("🎉 测试完成！请检查 Telegram 是否收到消息。")


if __name__ == "__main__":
    main()
