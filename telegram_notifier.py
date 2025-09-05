"""
telegram_notifier.py

Telegram 通知发送模块。
负责向 Telegram 发送网站监控状态通知。
"""

import requests
import time
from typing import Optional, Dict, Any
from telegram_config import load_config, is_telegram_configured


def send_telegram_message(message: str) -> bool:
    """
    发送消息到 Telegram。
    
    Args:
        message: 要发送的消息内容
        
    Returns:
        bool: 发送是否成功
    """
    if not is_telegram_configured():
        print("⚠️  Telegram 未配置或未启用，跳过通知发送")
        return False
    
    config = load_config()
    bot_token = config["bot_token"]
    chat_id = config["chat_id"]
    
    # Telegram Bot API URL
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # 消息数据
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",  # 支持 HTML 格式
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            print(f"✅ Telegram 通知发送成功: {message[:50]}...")
            return True
        else:
            print(f"❌ Telegram 发送失败: {result.get('description', '未知错误')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Telegram 发送异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Telegram 发送未知错误: {str(e)}")
        return False


def format_site_down_message(site_name: str, site_url: str, 
                           consecutive_failures: int, 
                           error_info: str = None) -> str:
    """
    格式化网站故障通知消息。
    
    Args:
        site_name: 网站名称
        site_url: 网站URL
        consecutive_failures: 连续失败次数
        error_info: 错误信息
        
    Returns:
        str: 格式化的消息
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    message = f"""🚨 <b>网站监控警报</b>

📊 <b>网站信息:</b>
• 名称: {site_name}
• URL: {site_url}
• 连续失败: {consecutive_failures} 次

⏰ <b>检测时间:</b> {timestamp}

⚠️ <b>状态:</b> 网站不可访问"""

    if error_info and error_info != "None":
        message += f"\n\n🔍 <b>错误详情:</b> {error_info}"
    
    message += "\n\n请及时检查网站状态！"
    
    return message


def format_site_recovery_message(site_name: str, site_url: str, 
                               latency_ms: int) -> str:
    """
    格式化网站恢复通知消息。
    
    Args:
        site_name: 网站名称
        site_url: 网站URL
        latency_ms: 响应延迟（毫秒）
        
    Returns:
        str: 格式化的消息
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    message = f"""✅ <b>网站恢复通知</b>

📊 <b>网站信息:</b>
• 名称: {site_name}
• URL: {site_url}
• 响应延迟: {latency_ms} ms

⏰ <b>恢复时间:</b> {timestamp}

🎉 <b>状态:</b> 网站已恢复正常访问"""
    
    return message


def send_site_down_alert(site_name: str, site_url: str, 
                        consecutive_failures: int, 
                        error_info: str = None) -> bool:
    """
    发送网站故障警报。
    
    Args:
        site_name: 网站名称
        site_url: 网站URL
        consecutive_failures: 连续失败次数
        error_info: 错误信息
        
    Returns:
        bool: 发送是否成功
    """
    message = format_site_down_message(site_name, site_url, consecutive_failures, error_info)
    return send_telegram_message(message)


def send_site_recovery_alert(site_name: str, site_url: str, 
                           latency_ms: int) -> bool:
    """
    发送网站恢复通知。
    
    Args:
        site_name: 网站名称
        site_url: 网站URL
        latency_ms: 响应延迟（毫秒）
        
    Returns:
        bool: 发送是否成功
    """
    message = format_site_recovery_message(site_name, site_url, latency_ms)
    return send_telegram_message(message)


def test_telegram_connection() -> bool:
    """
    测试 Telegram 连接是否正常。
    
    Returns:
        bool: 连接是否成功
    """
    if not is_telegram_configured():
        print("❌ Telegram 未配置或未启用")
        return False
    
    test_message = "🧪 UptimeGuard Telegram 通知测试消息\n\n如果您收到此消息，说明配置正确！"
    return send_telegram_message(test_message)
