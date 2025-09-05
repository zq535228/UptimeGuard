#!/usr/bin/env python3
"""
start_chat_bot.py

启动 Telegram 聊天机器人的便捷脚本。
用于获取 chat_id 并配置 Telegram 通知。
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_chat_bot import start_chat_bot, test_chat_bot


def main():
    """主函数"""
    print("🤖 UptimeGuard Telegram 聊天机器人")
    print("=" * 40)
    print()
    print("选择操作:")
    print("1. 启动聊天机器人 (获取 chat_id)")
    print("2. 测试 Telegram 通知")
    print("3. 退出")
    print()
    
    while True:
        try:
            choice = input("请输入选择 (1-3): ").strip()
            
            if choice == "1":
                print("\n🚀 启动聊天机器人...")
                start_chat_bot()
                break
            elif choice == "2":
                print("\n🧪 测试 Telegram 通知...")
                test_chat_bot()
                break
            elif choice == "3":
                print("\n👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入 1、2 或 3")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            break


if __name__ == "__main__":
    main()
