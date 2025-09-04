"""
monitor.py

监控与状态快照：周期性（或模拟）检查站点可用性，并将结果写入日志文件。
为便于演示，这里提供一个“模拟监控”实现：随机生成状态与延迟。
后续可替换为真实 HTTP 请求检查（如 requests/head）。
"""

import os
import time
import threading
import random
from typing import Dict, List, Any
from log_manager import get_log_manager


# 日志文件路径
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE_PATH = os.path.join(LOG_DIR, "uptime.log")


# 内存中的最近状态快照，供 UI 展示。
# 结构： {url: {"status": "up"|"down", "latency_ms": int, "timestamp": float}}
latest_status_snapshot: Dict[str, Dict[str, Any]] = {}


def ensure_log_file() -> None:
    """确保日志目录与文件存在。"""
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("")


def write_log_line(line: str) -> None:
    """写一行到日志（通过 LogManager：文件 + 内存）。"""
    ensure_log_file()
    manager = get_log_manager(LOG_FILE_PATH)
    manager.log_message(line)


def simulate_check(url: str) -> Dict[str, Any]:
    """模拟一次站点检查，返回结果字典。"""
    # 80% up，20% down；延迟 50-800ms 随机
    is_up = random.random() < 0.8
    latency_ms = random.randint(50, 800)
    status = "up" if is_up else "down"
    return {
        "http_status": 200 if is_up else 503,
        "html_keyword": "success" if is_up else "failure",
        "ssl_status": "up" if is_up else "down",
        "status": status,
        "latency_ms": latency_ms,
        "timestamp": time.time(),
        "http_status": 200 if is_up else 503,
        "error": None if is_up else "Simulated outage",
    }


def poll_once(sites: List[Dict[str, Any]]) -> None:
    """对所有站点执行一次模拟检测，写日志并更新快照。"""
    for site in sites:
        url = site.get("url", "")
        name = site.get("name", "")
        result = simulate_check(url)

        # 更新状态快照
        previous = latest_status_snapshot.get(url, {})
        previous_failures = int(previous.get("consecutive_failures", 0) or 0)
        new_failures = previous_failures + 1 if result["status"] == "down" else 0

        latest_status_snapshot[url] = {
            "name": name,
            "status": result["status"],
            "latency_ms": result["latency_ms"],
            "timestamp": result["timestamp"],
            "consecutive_failures": new_failures,
        }

        # 记录日志（简化文本格式，便于新手查看）
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(result["timestamp"]))
        log_line = f"[{ts_str}] name={name} url={url} status={result['status']} http={result['http_status']} latency_ms={result['latency_ms']} error={result['error']}"
        write_log_line(log_line)


def start_background_polling(get_sites_callable, interval_seconds: int = 30) -> threading.Thread:
    """
    启动后台线程，按固定间隔轮询站点。
    get_sites_callable: 一个可调用对象，返回当前站点列表（例如 storage.load_sites）。
    返回线程对象，以便在 app 退出时进行控制。
    """
    ensure_log_file()

    def _loop():
        while True:
            try:
                sites = get_sites_callable()
                poll_once(sites)
            except Exception as e:
                # 任何异常写日志但不中断线程
                write_log_line(f"[ERROR] polling exception: {e}")
            time.sleep(interval_seconds)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t


