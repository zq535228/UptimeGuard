"""
log_manager.py

提供一个简单的日志管理器：
- 记录日志到内存（队列与历史列表）与文件
- 支持限制历史长度并定期清理过大的日志文件
"""

from __future__ import annotations

import os
from datetime import datetime
from queue import Queue
from typing import List, Optional


class LogManager:
    """日志管理器：内存缓冲 + 文件写入。

    参数：
    - log_file_path: 日志文件路径
    - max_log_history: 内存保存的最大行数
    """

    def __init__(self, log_file_path: str, max_log_history: int = 2000) -> None:
        self.log_file_path = log_file_path
        self.max_log_history = max_log_history
        self.log_queue: Queue[str] = Queue()
        self.log_history: List[str] = []

        # 确保目录存在
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w', encoding='utf-8'):
                pass

    def log_message(self, message: str) -> None:
        """记录日志消息（写入队列、历史与文件，并控制台输出）。"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        # 添加到队列（用于实时显示）
        self.log_queue.put(log_entry)

        # 添加到历史记录
        self.log_history.append(log_entry)

        # 限制历史记录长度
        if len(self.log_history) > self.max_log_history:
            self.log_history = self.log_history[-self.max_log_history:]

        # 写入日志文件
        self._write_log_to_file(log_entry)

        # 控制台输出
        print(log_entry)

    def _write_log_to_file(self, log_entry: str) -> None:
        """将日志写入文件。"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"写入日志文件失败: {e}")

    def _cleanup_old_logs(self) -> None:
        """清理过旧的日志文件内容（超过 5000 行则截断为后 2500 行）。"""
        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                if len(lines) > 5000:
                    lines = lines[-2500:]
                    with open(self.log_file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
        except Exception as e:
            print(f"清理日志文件失败: {e}")

    def drain_queue_as_text(self) -> str:
        """取出队列里所有新日志，拼接为文本。若无则返回空串。"""
        chunks: List[str] = []
        while not self.log_queue.empty():
            chunks.append(self.log_queue.get())
        return "\n".join(chunks)

    def get_history_text(self, n: Optional[int] = None) -> str:
        """获取历史日志文本，默认返回全部（最多 max_log_history）。"""
        if not self.log_history:
            return "(暂无日志)\n"
        if n is None:
            n = self.max_log_history
        return "\n".join(self.log_history[-n:]) + "\n"


_singleton: Optional[LogManager] = None


def get_log_manager(log_file_path: str) -> LogManager:
    """获取（或初始化）全局日志管理器单例。"""
    global _singleton
    if _singleton is None:
        _singleton = LogManager(log_file_path=log_file_path)
    return _singleton


