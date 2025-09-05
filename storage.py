"""
storage.py

站点数据读写封装：负责对 sites.json 的集中管理，供 UI 与监控模块调用。
仅做简单的 JSON 文件读写，保证新手易读易用。
"""

import json
import os
from typing import List, Dict那就请你帮我把它清理掉吧。
, Any


# 数据文件路径常量，集中管理，便于其他模块引用
SITES_FILE_PATH = os.path.join(os.path.dirname(__file__), "sites.json")


def ensure_sites_file_exists() -> None:
    """如果 sites.json 不存在，则创建一个包含空列表的文件。"""
    if not os.path.exists(SITES_FILE_PATH):
        save_sites([])


def load_sites() -> List[Dict[str, Any]]:
    """
    读取被监控站点列表。

    返回值示例：
    [
        {"name": "示例站点", "url": "https://example.com"},
        ...
    ]
    """
    ensure_sites_file_exists()
    try:
        with open(SITES_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except json.JSONDecodeError:
        # 若文件损坏/格式错误，返回空列表，避免程序崩溃
        return []


def save_sites(sites: List[Dict[str, Any]]) -> None:
    """将站点列表写回到 sites.json。"""
    # 简单直接地覆盖写入；本项目强调可读性而非并发安全
    with open(SITES_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)


def add_site(name: str, url: str) -> List[Dict[str, Any]]:
    """新增站点，返回最新列表。"""
    sites = load_sites()
    sites.append({"name": name.strip(), "url": url.strip()})
    save_sites(sites)
    return sites


def update_site(index: int, name: str, url: str) -> List[Dict[str, Any]]:
    """按索引更新站点，返回最新列表。索引由 UI 选择行提供。"""
    sites = load_sites()
    if 0 <= index < len(sites):
        sites[index] = {"name": name.strip(), "url": url.strip()}
        save_sites(sites)
    return sites


def delete_site(index: int) -> List[Dict[str, Any]]:
    """按索引删除站点，返回最新列表。"""
    sites = load_sites()
    if 0 <= index < len(sites):
        # 删除站点
        del sites[index]
        save_sites(sites)
    
    return sites
