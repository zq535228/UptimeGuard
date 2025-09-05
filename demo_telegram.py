#!/usr/bin/env python3
"""
demo_telegram.py

演示 Telegram 通知功能的脚本。
模拟网站监控场景，展示连续失败检测和通知发送。
"""

import time
import random
from telegram_config import update_config, load_config
from telegram_notifier import send_site_down_alert, send_site_recovery_alert


def demo_telegram_notifications():
    """演示 Telegram 通知功能"""
    print("🎭 UptimeGuard Telegram 通知功能演示")
    print("=" * 60)
    
    # 检查是否已配置
    config = load_config()
    if not config["bot_token"] or not config["chat_id"]:
        print("❌ 请先配置 Telegram Bot Token 和 Chat ID")
        print("   可以通过以下方式配置：")
        print("   1. 在 UI 中配置")
        print("   2. 设置环境变量")
        print("   3. 运行以下命令：")
        print()
        print("   python -c \"")
        print("   from telegram_config import update_config")
        print("   update_config(bot_token='YOUR_BOT_TOKEN', chat_id='YOUR_CHAT_ID', enabled=True)")
        print("   \"")
        return
    
    print("✅ Telegram 已配置，开始演示...")
    print()
    
    # 模拟网站监控场景
    site_name = "演示网站"
    site_url = "https://demo.example.com"
    failure_threshold = 10
    
    print(f"📊 监控网站: {site_name} ({site_url})")
    print(f"🎯 失败阈值: {failure_threshold} 次")
    print()
    
    # 模拟连续失败
    print("🚨 模拟连续失败场景...")
    for i in range(1, failure_threshold + 1):
        print(f"   第 {i} 次检测: 失败 ❌")
        time.sleep(0.5)
    
    print()
    print("📱 发送故障警报...")
    if send_site_down_alert(
        site_name=site_name,
        site_url=site_url,
        consecutive_failures=failure_threshold,
        error_info="连接超时 - 演示场景"
    ):
        print("✅ 故障警报发送成功！")
    else:
        print("❌ 故障警报发送失败！")
    
    print()
    time.sleep(2)
    
    # 模拟恢复
    print("✅ 模拟网站恢复...")
    print("   检测: 成功 ✅")
    print()
    print("📱 发送恢复通知...")
    if send_site_recovery_alert(
        site_name=site_name,
        site_url=site_url,
        latency_ms=random.randint(100, 500)
    ):
        print("✅ 恢复通知发送成功！")
    else:
        print("❌ 恢复通知发送失败！")
    
    print()
    print("🎉 演示完成！请检查 Telegram 是否收到消息。")


def setup_demo_config():
    """设置演示配置（需要用户提供真实的 Token 和 Chat ID）"""
    print("🔧 设置演示配置")
    print("=" * 30)
    
    bot_token = input("请输入 Telegram Bot Token: ").strip()
    chat_id = input("请输入 Chat ID: ").strip()
    
    if not bot_token or not chat_id:
        print("❌ 配置信息不完整")
        return False
    
    try:
        update_config(
            bot_token=bot_token,
            chat_id=chat_id,
            enabled=True,
            failure_threshold=10
        )
        print("✅ 配置保存成功！")
        return True
    except Exception as e:
        print(f"❌ 配置保存失败: {e}")
        return False


if __name__ == "__main__":
    print("选择操作：")
    print("1. 运行演示")
    print("2. 设置配置")
    print("3. 退出")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        demo_telegram_notifications()
    elif choice == "2":
        if setup_demo_config():
            print("\n配置完成，现在可以运行演示了！")
            demo_telegram_notifications()
    elif choice == "3":
        print("👋 再见！")
    else:
        print("❌ 无效选择")
