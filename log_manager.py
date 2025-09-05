"""
log_manager.py

提供一个简单的日志管理器：
- 记录日志到内存（队列与历史列表）与文件
- 支持限制历史长度并定期清理过大的日志文件
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
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
        self.last_cleanup_time = 0  # 上次清理时间（时间戳）
        self.cleanup_interval = 3600  # 清理间隔：1小时（秒）
        self.log_retention_days = 3  # 日志保留天数

        # 确保目录存在
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'w', encoding='utf-8'):
                pass

    def log_message(self, message: str) -> None:
        """记录日志消息（写入队列、历史与文件，并控制台输出）。"""
        # 使用完整的日期时间格式，便于日志清理
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

        # 定期清理旧日志（每小时检查一次）
        current_time = time.time()
        if current_time - self.last_cleanup_time > self.cleanup_interval:
            self._cleanup_old_logs_by_time()
            self.last_cleanup_time = current_time

        # 控制台输出
        print(log_entry)

    def _write_log_to_file(self, log_entry: str) -> None:
        """将日志写入文件。"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"写入日志文件失败: {e}")

    def _cleanup_old_logs_by_time(self) -> None:
        """基于时间清理旧日志，只保留指定天数内的日志。"""
        try:
            if not os.path.exists(self.log_file_path):
                return
                
            # 计算保留的截止时间
            cutoff_time = datetime.now() - timedelta(days=self.log_retention_days)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # 读取所有日志行
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return
                
            # 过滤出需要保留的日志行
            kept_lines = []
            removed_count = 0
            
            for line in lines:
                # 尝试从日志行中提取时间戳
                if self._should_keep_log_line(line, cutoff_timestamp):
                    kept_lines.append(line)
                else:
                    removed_count += 1
            
            # 如果删除了日志，重写文件
            if removed_count > 0:
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.writelines(kept_lines)
                print(f"🧹 日志清理完成：删除了 {removed_count} 行旧日志，保留了 {len(kept_lines)} 行")
                
        except Exception as e:
            print(f"清理日志文件失败: {e}")

    def _should_keep_log_line(self, line: str, cutoff_timestamp: float) -> bool:
        """判断日志行是否应该保留（基于时间戳）。"""
        try:
            # 日志格式：[时间戳] 消息内容
            # 例如：[2025-09-05 05:42:37] name=检验大叔官网 url=https://www.jianyandashu.com status=up
            if line.startswith('[') and ']' in line:
                # 提取时间戳部分
                timestamp_str = line[1:line.index(']')]
                
                # 尝试解析时间戳
                if ' ' in timestamp_str and ':' in timestamp_str:
                    # 格式：2025-09-05 05:42:37
                    try:
                        log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        return log_time.timestamp() >= cutoff_timestamp
                    except ValueError:
                        pass
                elif ':' in timestamp_str:
                    # 格式：05:42:37（只有时间，没有日期）
                    # 对于这种格式，我们假设是今天的日志，直接保留
                    return True
                    
            # 如果无法解析时间戳，保留该行（避免误删重要日志）
            return True
            
        except Exception:
            # 解析失败时保留该行
            return True

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

    def cleanup_logs_now(self) -> str:
        """立即执行日志清理，返回清理结果信息。"""
        try:
            if not os.path.exists(self.log_file_path):
                return "日志文件不存在"
                
            # 计算保留的截止时间
            cutoff_time = datetime.now() - timedelta(days=self.log_retention_days)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # 读取所有日志行
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return "日志文件为空"
                
            # 过滤出需要保留的日志行
            kept_lines = []
            removed_count = 0
            
            for line in lines:
                if self._should_keep_log_line(line, cutoff_timestamp):
                    kept_lines.append(line)
                else:
                    removed_count += 1
            
            # 如果删除了日志，重写文件
            if removed_count > 0:
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.writelines(kept_lines)
                return f"🧹 日志清理完成：删除了 {removed_count} 行旧日志，保留了 {len(kept_lines)} 行"
            else:
                return f"📝 日志文件正常，共 {len(kept_lines)} 行，无需清理"
                
        except Exception as e:
            return f"❌ 清理日志失败: {str(e)}"


_singleton: Optional[LogManager] = None


def get_log_manager(log_file_path: str) -> LogManager:
    """获取（或初始化）全局日志管理器单例。"""
    global _singleton
    if _singleton is None:
        _singleton = LogManager(log_file_path=log_file_path)
    return _singleton


