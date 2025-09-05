#!/usr/bin/env python3
"""
final_demo.py

最终功能演示脚本，展示完整的 Telegram 通知功能。
"""

import time
import random
from telegram_config import update_config, load_config, is_telegram_configured
from telegram_notifier import send_site_down_alert, send_site_recovery_alert, test_telegram_connection


def show_welcome():
    """显示欢迎信息"""
    print("🎉 UptimeGuard Telegram 通知功能演示")
    print("=" * 60)
    print("✅ 功能已成功实现：")
    print("   • 连续失败检测（默认阈值：10次）")
    print("   • Telegram 故障警报")
    print("   • Telegram 恢复通知")
    print("   • Web UI 配置界面")
    print("   • 完整的日志记录")
    print()


def show_config_status():
    """显示配置状态"""
    print("🔧 当前配置状态：")
    config = load_config()
    print(f"   Bot Token: {'✅ 已配置' if config['bot_token'] else '❌ 未配置'}")
    print(f"   Chat ID: {'✅ 已配置' if config['chat_id'] else '❌ 未配置'}")
    print(f"   启用状态: {'✅ 已启用' if config['enabled'] else '❌ 未启用'}")
    print(f"   失败阈值: {config['failure_threshold']} 次")
    print(f"   配置完整: {'✅ 是' if is_telegram_configured() else '❌ 否'}")
    print()


def show_usage_instructions():
    """显示使用说明"""
    print("📖 使用说明：")
    print("1. 启动应用：")
    print("   source .venv/bin/activate")
    print("   python app.py")
    print()
    print("2. 访问 Web 界面：")
    print("   http://127.0.0.1:7860")
    print()
    print("3. 配置 Telegram：")
    print("   • 展开 '🔔 Telegram 通知配置' 区域")
    print("   • 填写 Bot Token 和 Chat ID")
    print("   • 点击 '🧪 测试连接' 验证")
    print("   • 点击 '💾 保存配置' 保存")
    print()
    print("4. 监控功能：")
    print("   • 应用会自动监控配置的网站")
    print("   • 连续失败达到阈值时发送警报")
    print("   • 网站恢复时发送恢复通知")
    print()


def show_telegram_setup_guide():
    """显示 Telegram 设置指南"""
    print("🔔 Telegram 设置指南：")
    print("1. 创建 Bot：")
    print("   • 在 Telegram 中搜索 @BotFather")
    print("   • 发送 /newbot 命令")
    print("   • 按提示创建机器人")
    print("   • 复制获得的 Bot Token")
    print()
    print("2. 获取 Chat ID：")
    print("   • 将机器人添加到群组或开始私聊")
    print("   • 发送任意消息给机器人")
    print("   • 访问：https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("   • 在返回的 JSON 中找到 chat.id")
    print()


def show_file_structure():
    """显示文件结构"""
    print("📁 项目文件结构：")
    files = [
        "app.py - 应用入口",
        "monitor.py - 监控逻辑（已集成 Telegram 通知）",
        "ui.py - Web 界面（已添加配置界面）",
        "storage.py - 数据存储",
        "telegram_config.py - Telegram 配置管理",
        "telegram_notifier.py - Telegram 通知发送",
        "test_telegram.py - 测试脚本",
        "demo_telegram.py - 演示脚本",
        "status_check.py - 状态检查脚本",
        "TELEGRAM_SETUP.md - 详细设置指南",
        "FEATURE_SUMMARY.md - 功能总结文档"
    ]
    
    for file in files:
        print(f"   • {file}")
    print()


def show_monitoring_example():
    """显示监控示例"""
    print("📊 监控示例（模拟场景）：")
    print("假设监控网站：https://example.com")
    print("连续失败阈值：10 次")
    print()
    
    print("场景 1：连续失败")
    for i in range(1, 11):
        print(f"   第 {i} 次检测: 失败 ❌")
        time.sleep(0.3)
    
    print("   → 达到阈值，发送 Telegram 故障警报！")
    print()
    
    print("场景 2：网站恢复")
    print("   第 11 次检测: 成功 ✅ (延迟: 150ms)")
    print("   → 发送 Telegram 恢复通知！")
    print()


def main():
    """主函数"""
    show_welcome()
    show_config_status()
    show_usage_instructions()
    show_telegram_setup_guide()
    show_file_structure()
    show_monitoring_example()
    
    print("🎯 核心功能已实现：")
    print("   ✅ 当 consecutive_failures > 10 时发送 Telegram 通知")
    print("   ✅ 网站恢复时发送恢复通知")
    print("   ✅ 完整的 Web UI 配置界面")
    print("   ✅ 详细的日志记录和错误处理")
    print()
    print("🚀 应用正在运行中，访问 http://127.0.0.1:7860 开始使用！")


if __name__ == "__main__":
    main()
