"""
telegram_config.py

Telegram 通知配置管理模块。
负责管理 Telegram Bot Token 和 Chat ID 的配置，支持从环境变量或配置文件读取。
"""

import os
import json
from typing import Optional, Dict, Any


# 配置文件路径
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "telegram_config.json")


def ensure_config_file() -> None:
    """确保配置文件存在，如果不存在则创建默认配置。"""
    if not os.path.exists(CONFIG_FILE_PATH):
        default_config = {
            "bot_token": "",
            "chat_id": "",
            "enabled": False,
            "failure_threshold": 10
        }
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)


def load_config() -> Dict[str, Any]:
    """
    加载 Telegram 配置。
    优先从环境变量读取，其次从配置文件读取。
    
    返回配置字典，包含：
    - bot_token: Telegram Bot Token
    - chat_id: 目标聊天ID
    - enabled: 是否启用通知
    - failure_threshold: 连续失败阈值
    """
    ensure_config_file()
    
    # 从环境变量读取（优先级更高）
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    enabled = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    failure_threshold = int(os.getenv("TELEGRAM_FAILURE_THRESHOLD", "10"))
    
    # 如果环境变量为空，从配置文件读取
    if not bot_token or not chat_id:
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 只有当环境变量为空时才使用配置文件的值
                if not bot_token:
                    bot_token = config.get("bot_token", "")
                if not chat_id:
                    chat_id = config.get("chat_id", "")
                # enabled 和 failure_threshold 总是从配置文件读取（除非环境变量明确设置）
                if not os.getenv("TELEGRAM_ENABLED"):
                    enabled = config.get("enabled", False)
                if not os.getenv("TELEGRAM_FAILURE_THRESHOLD"):
                    failure_threshold = config.get("failure_threshold", 10)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    return {
        "bot_token": bot_token,
        "chat_id": chat_id,
        "enabled": enabled,
        "failure_threshold": failure_threshold
    }


def save_config(config: Dict[str, Any]) -> None:
    """保存配置到文件。"""
    ensure_config_file()
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def update_config(bot_token: str = None, chat_id: str = None, 
                 enabled: bool = None, failure_threshold: int = None) -> Dict[str, Any]:
    """
    更新配置并保存。
    只更新提供的参数，其他参数保持不变。
    """
    config = load_config()
    
    if bot_token is not None:
        config["bot_token"] = bot_token
    if chat_id is not None:
        config["chat_id"] = chat_id
    if enabled is not None:
        config["enabled"] = enabled
    if failure_threshold is not None:
        config["failure_threshold"] = failure_threshold
    
    save_config(config)
    return config


def is_telegram_configured() -> bool:
    """检查 Telegram 是否已正确配置。"""
    config = load_config()
    return bool(config["bot_token"] and config["chat_id"] and config["enabled"])


def get_failure_threshold() -> int:
    """获取连续失败阈值。"""
    config = load_config()
    return config["failure_threshold"]
