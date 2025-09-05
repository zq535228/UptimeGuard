"""
telegram_chat_bot.py

Telegram 聊天机器人模块。
用于接收用户消息并自动获取 chat_id，方便配置监控通知。
"""

import requests
import time
import json
from typing import Optional, Dict, Any
from telegram_config import load_config, update_config


def get_bot_info(bot_token: str) -> Optional[Dict[str, Any]]:
    """
    获取机器人信息。
    
    Args:
        bot_token: 机器人 Token
        
    Returns:
        Dict: 机器人信息，如果失败返回 None
    """
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            return result.get("result")
        else:
            print(f"❌ 获取机器人信息失败: {result.get('description', '未知错误')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取机器人信息异常: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 获取机器人信息未知错误: {str(e)}")
        return None


def get_updates(bot_token: str, offset: int = 0) -> Optional[list]:
    """
    获取机器人收到的消息更新。
    
    Args:
        bot_token: 机器人 Token
        offset: 偏移量，用于获取新消息
        
    Returns:
        list: 消息列表，如果失败返回 None
    """
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    params = {
        "offset": offset,
        "timeout": 30,  # 长轮询30秒
        "allowed_updates": ["message"]  # 只接收消息更新
    }
    
    try:
        response = requests.get(url, params=params, timeout=35)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            return result.get("result", [])
        else:
            print(f"❌ 获取消息失败: {result.get('description', '未知错误')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取消息异常: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 获取消息未知错误: {str(e)}")
        return None


def send_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    发送消息到指定聊天。
    
    Args:
        bot_token: 机器人 Token
        chat_id: 聊天 ID
        message: 消息内容
        
    Returns:
        bool: 发送是否成功
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            return True
        else:
            print(f"❌ 发送消息失败: {result.get('description', '未知错误')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 发送消息异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 发送消息未知错误: {str(e)}")
        return False


def process_message(update: Dict[str, Any], bot_token: str) -> Optional[str]:
    """
    处理收到的消息。
    
    Args:
        update: 消息更新数据
        bot_token: 机器人 Token
        
    Returns:
        str: 处理后的 chat_id，如果不需要保存则返回 None
    """
    message = update.get("message", {})
    chat = message.get("chat", {})
    text = message.get("text", "")
    chat_id = str(chat.get("id", ""))
    user_name = message.get("from", {}).get("first_name", "未知用户")
    
    print(f"📨 收到来自 {user_name} 的消息: {text}")
    print(f"🆔 聊天 ID: {chat_id}")
    
    # 发送欢迎消息
    welcome_message = f"""👋 你好 {user_name}！

🤖 我是 UptimeGuard 监控机器人。

📊 <b>你的聊天信息：</b>
• 聊天 ID: <code>{chat_id}</code>
• 用户名: {user_name}

✅ 聊天 ID 已自动获取并保存到配置中！

现在你可以：
• 发送任意消息测试通知功能
• 在 UptimeGuard 中启用 Telegram 通知
• 监控网站状态变化时会收到通知

💡 <b>提示：</b> 你可以复制上面的聊天 ID 用于手动配置。"""
    
    # 发送回复消息
    if send_message(bot_token, chat_id, welcome_message):
        print(f"✅ 已向 {user_name} 发送欢迎消息")
        return chat_id
    else:
        print(f"❌ 向 {user_name} 发送消息失败")
        return None


def start_chat_bot():
    """
    启动聊天机器人，监听消息并自动获取 chat_id。
    """
    print("🤖 启动 UptimeGuard Telegram 聊天机器人...")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    bot_token = config.get("bot_token", "")
    
    if not bot_token:
        print("❌ 错误: 未找到 Telegram Bot Token")
        print("请先在 telegram_config.json 中配置 bot_token")
        return
    
    # 获取机器人信息
    bot_info = get_bot_info(bot_token)
    if not bot_info:
        print("❌ 无法连接到 Telegram 机器人，请检查 Token 是否正确")
        return
    
    bot_name = bot_info.get("first_name", "UptimeGuard Bot")
    bot_username = bot_info.get("username", "")
    
    print(f"✅ 机器人连接成功: {bot_name} (@{bot_username})")
    print(f"🔗 机器人链接: https://t.me/{bot_username}")
    print()
    print("📱 请向机器人发送任意消息来获取聊天 ID")
    print("⏹️  按 Ctrl+C 停止机器人")
    print("=" * 50)
    
    # 获取当前配置的 chat_id
    current_chat_id = config.get("chat_id", "")
    if current_chat_id:
        print(f"ℹ️  当前已配置的聊天 ID: {current_chat_id}")
        print("💡 发送消息后，新的聊天 ID 将覆盖当前配置")
        print()
    
    last_update_id = 0
    saved_chat_ids = set()  # 记录已保存的聊天 ID
    
    try:
        while True:
            # 获取新消息
            updates = get_updates(bot_token, last_update_id + 1)
            
            if updates is None:
                print("⚠️  获取消息失败，5秒后重试...")
                time.sleep(5)
                continue
            
            # 处理每条消息
            for update in updates:
                update_id = update.get("update_id", 0)
                last_update_id = max(last_update_id, update_id)
                
                # 只处理消息类型的更新
                if "message" in update:
                    chat_id = process_message(update, bot_token)
                    
                    # 如果成功获取到 chat_id 且未保存过，则保存到配置
                    if chat_id and chat_id not in saved_chat_ids:
                        print(f"💾 保存聊天 ID: {chat_id}")
                        
                        # 更新配置
                        new_config = update_config(chat_id=chat_id, enabled=True)
                        
                        if new_config.get("chat_id") == chat_id:
                            print("✅ 聊天 ID 已成功保存到配置文件中")
                            saved_chat_ids.add(chat_id)
                        else:
                            print("❌ 保存聊天 ID 失败")
            
            # 如果没有新消息，等待一下再继续
            if not updates:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n\n🛑 机器人已停止")
        print("=" * 50)
        
        # 显示最终配置
        final_config = load_config()
        final_chat_id = final_config.get("chat_id", "")
        
        if final_chat_id:
            print(f"✅ 最终配置的聊天 ID: {final_chat_id}")
            print("🎉 现在你可以在 UptimeGuard 中启用 Telegram 通知了！")
        else:
            print("⚠️  未获取到聊天 ID，请重新运行机器人并发送消息")
        
        print("\n💡 提示: 运行 'python test_telegram.py' 测试通知功能")


def test_chat_bot():
    """
    测试聊天机器人功能。
    """
    print("🧪 测试 Telegram 聊天机器人...")
    
    config = load_config()
    bot_token = config.get("bot_token", "")
    chat_id = config.get("chat_id", "")
    
    if not bot_token:
        print("❌ 未配置 Bot Token")
        return False
    
    if not chat_id:
        print("❌ 未配置 Chat ID，请先运行聊天机器人获取")
        return False
    
    # 测试发送消息
    test_message = """🧪 <b>UptimeGuard 测试消息</b>

✅ 如果你收到这条消息，说明 Telegram 通知配置正确！

📊 <b>配置信息：</b>
• 机器人: 已连接
• 聊天 ID: <code>{}</code>
• 状态: 正常工作

🎉 现在你可以接收网站监控通知了！""".format(chat_id)
    
    if send_message(bot_token, chat_id, test_message):
        print("✅ 测试消息发送成功！")
        return True
    else:
        print("❌ 测试消息发送失败")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_chat_bot()
    else:
        start_chat_bot()
