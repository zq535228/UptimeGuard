"""
notification_tracker.py

通知状态跟踪模块。
负责跟踪每个网站的最后通知状态，避免重复发送相同的通知消息。
"""

import os
import json
import time
from typing import Dict, Any, Optional


class NotificationTracker:
    """通知状态跟踪器"""
    
    def __init__(self, state_file_path: str = None):
        """
        初始化通知跟踪器
        
        Args:
            state_file_path: 状态文件路径，如果为None则使用默认路径
        """
        if state_file_path is None:
            self.state_file_path = os.path.join(os.path.dirname(__file__), "notification_state.json")
        else:
            self.state_file_path = state_file_path
        
        # 内存中的状态缓存
        self._state_cache: Dict[str, Dict[str, Any]] = {}
        self._load_state()
    
    def _load_state(self) -> None:
        """从文件加载通知状态"""
        try:
            if os.path.exists(self.state_file_path):
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    self._state_cache = json.load(f)
            else:
                self._state_cache = {}
        except (json.JSONDecodeError, FileNotFoundError):
            self._state_cache = {}
    
    def _save_state(self) -> None:
        """保存通知状态到文件"""
        try:
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(self._state_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存通知状态失败: {str(e)}")
    
    def get_last_notification_state(self, site_url: str) -> Optional[Dict[str, Any]]:
        """
        获取网站的最后通知状态
        
        Args:
            site_url: 网站URL
            
        Returns:
            最后通知状态字典，包含：
            - status: 最后通知的状态（"down" 或 "up"）
            - timestamp: 最后通知时间
            - consecutive_failures: 最后通知时的连续失败次数
        """
        return self._state_cache.get(site_url)
    
    def should_send_down_notification(self, site_url: str, current_status: str, 
                                    consecutive_failures: int, failure_threshold: int) -> bool:
        """
        判断是否应该发送故障通知
        
        Args:
            site_url: 网站URL
            current_status: 当前状态
            consecutive_failures: 当前连续失败次数
            failure_threshold: 失败阈值
            
        Returns:
            bool: 是否应该发送故障通知
        """
        # 如果当前状态不是故障，不发送故障通知
        if current_status != "down":
            return False
        
        # 如果连续失败次数未达到阈值，不发送通知
        if consecutive_failures < failure_threshold:
            return False
        
        # 获取最后通知状态
        last_state = self.get_last_notification_state(site_url)
        
        # 如果没有历史状态，可以发送通知
        if last_state is None:
            return True
        
        # 如果最后通知的是故障状态，且连续失败次数相同，不重复发送
        if (last_state.get("status") == "down" and 
            last_state.get("consecutive_failures") == consecutive_failures):
            return False
        
        # 如果最后通知的是故障状态，但连续失败次数增加了，可以发送更新通知
        if (last_state.get("status") == "down" and 
            consecutive_failures > last_state.get("consecutive_failures", 0)):
            return True
        
        # 如果最后通知的是正常状态，现在变成故障，可以发送通知
        if last_state.get("status") == "up":
            return True
        
        return False
    
    def should_send_recovery_notification(self, site_url: str, current_status: str, 
                                        previous_status: str, previous_failures: int, 
                                        failure_threshold: int) -> bool:
        """
        判断是否应该发送恢复通知
        
        Args:
            site_url: 网站URL
            current_status: 当前状态
            previous_status: 之前的状态
            previous_failures: 之前的连续失败次数
            failure_threshold: 失败阈值
            
        Returns:
            bool: 是否应该发送恢复通知
        """
        # 如果当前状态不是正常，不发送恢复通知
        if current_status != "up":
            return False
        
        # 如果之前状态不是故障，不发送恢复通知
        if previous_status != "down":
            return False
        
        # 如果之前的连续失败次数未达到阈值，不发送恢复通知
        if previous_failures < failure_threshold:
            return False
        
        # 获取最后通知状态
        last_state = self.get_last_notification_state(site_url)
        
        # 如果没有历史状态，可以发送恢复通知
        if last_state is None:
            return True
        
        # 如果最后通知的是恢复状态，不重复发送
        if last_state.get("status") == "up":
            return False
        
        # 如果最后通知的是故障状态，现在恢复，可以发送恢复通知
        if last_state.get("status") == "down":
            return True
        
        return False
    
    def update_notification_state(self, site_url: str, status: str, 
                                consecutive_failures: int = 0) -> None:
        """
        更新网站的通知状态
        
        Args:
            site_url: 网站URL
            status: 当前状态
            consecutive_failures: 连续失败次数
        """
        self._state_cache[site_url] = {
            "status": status,
            "timestamp": time.time(),
            "consecutive_failures": consecutive_failures
        }
        self._save_state()
    
    def clear_site_state(self, site_url: str) -> None:
        """
        清除网站的通知状态（用于网站被删除时）
        
        Args:
            site_url: 网站URL
        """
        if site_url in self._state_cache:
            del self._state_cache[site_url]
            self._save_state()
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有网站的通知状态
        
        Returns:
            所有网站的通知状态字典
        """
        return self._state_cache.copy()
    
    def cleanup_old_states(self, max_age_hours: int = 24 * 7) -> None:
        """
        清理过期的通知状态（超过指定小时数的状态）
        
        Args:
            max_age_hours: 最大保留时间（小时）
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        sites_to_remove = []
        for site_url, state in self._state_cache.items():
            if current_time - state.get("timestamp", 0) > max_age_seconds:
                sites_to_remove.append(site_url)
        
        for site_url in sites_to_remove:
            del self._state_cache[site_url]
        
        if sites_to_remove:
            self._save_state()
            print(f"🧹 清理了 {len(sites_to_remove)} 个过期的通知状态")


# 全局通知跟踪器实例
_notification_tracker = None


def get_notification_tracker() -> NotificationTracker:
    """
    获取全局通知跟踪器实例
    
    Returns:
        NotificationTracker: 通知跟踪器实例
    """
    global _notification_tracker
    if _notification_tracker is None:
        _notification_tracker = NotificationTracker()
    return _notification_tracker


def should_send_down_notification(site_url: str, current_status: str, 
                                consecutive_failures: int, failure_threshold: int) -> bool:
    """
    判断是否应该发送故障通知（便捷函数）
    
    Args:
        site_url: 网站URL
        current_status: 当前状态
        consecutive_failures: 当前连续失败次数
        failure_threshold: 失败阈值
        
    Returns:
        bool: 是否应该发送故障通知
    """
    tracker = get_notification_tracker()
    return tracker.should_send_down_notification(
        site_url, current_status, consecutive_failures, failure_threshold
    )


def should_send_recovery_notification(site_url: str, current_status: str, 
                                    previous_status: str, previous_failures: int, 
                                    failure_threshold: int) -> bool:
    """
    判断是否应该发送恢复通知（便捷函数）
    
    Args:
        site_url: 网站URL
        current_status: 当前状态
        previous_status: 之前的状态
        previous_failures: 之前的连续失败次数
        failure_threshold: 失败阈值
        
    Returns:
        bool: 是否应该发送恢复通知
    """
    tracker = get_notification_tracker()
    return tracker.should_send_recovery_notification(
        site_url, current_status, previous_status, previous_failures, failure_threshold
    )


def update_notification_state(site_url: str, status: str, 
                            consecutive_failures: int = 0) -> None:
    """
    更新网站的通知状态（便捷函数）
    
    Args:
        site_url: 网站URL
        status: 当前状态
        consecutive_failures: 连续失败次数
    """
    tracker = get_notification_tracker()
    tracker.update_notification_state(site_url, status, consecutive_failures)


def clear_site_state(site_url: str) -> None:
    """
    清除网站的通知状态（便捷函数）
    
    Args:
        site_url: 网站URL
    """
    tracker = get_notification_tracker()
    tracker.clear_site_state(site_url)


if __name__ == "__main__":
    # 测试代码
    tracker = get_notification_tracker()
    
    # 测试故障通知逻辑
    print("测试故障通知逻辑:")
    print(f"首次故障: {should_send_down_notification('https://example.com', 'down', 10, 10)}")
    print(f"相同故障: {should_send_down_notification('https://example.com', 'down', 10, 10)}")
    print(f"故障次数增加: {should_send_down_notification('https://example.com', 'down', 15, 10)}")
    
    # 测试恢复通知逻辑
    print("\n测试恢复通知逻辑:")
    print(f"从故障恢复: {should_send_recovery_notification('https://example.com', 'up', 'down', 10, 10)}")
    print(f"重复恢复: {should_send_recovery_notification('https://example.com', 'up', 'down', 10, 10)}")
