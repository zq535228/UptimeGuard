"""
ui.py

Gradio 界面定义：包含两个主要区域——网站列表与日志信息。
支持在 UI 中对被监控网站进行增删改，并实时查看模拟日志。
"""

from typing import List, Dict, Any
import time
import gradio as gr
from docker_utils import is_docker_environment

from storage import load_sites
from monitor import latest_status_snapshot, LOG_FILE_PATH
from log_manager import get_log_manager


def _sites_to_table_rows(sites: List[Dict[str, Any]]) -> List[List[Any]]:
    """将站点与快照整合为表格需要的二维数组。"""
    rows: List[List[Any]] = []
    for site in sites:
        name = site.get("name", "")
        url = site.get("url", "")
        snap = latest_status_snapshot.get(url, {})
        http_status = snap.get("http_status", "-")
        html_keyword = snap.get("html_keyword", "-")
        ssl_status = snap.get("ssl_status", "-")
        status = snap.get("status", "-")
        consecutive_failures = snap.get("consecutive_failures", 0)
        latency = snap.get("latency_ms", "-")
        ts = snap.get("timestamp")
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) if ts else "-"
        rows.append([name, url, http_status, html_keyword, ssl_status,status, consecutive_failures, latency, ts_str])
    return rows


def read_latest_logs(n: int = 200) -> str:
    """读取日志文件的最新 N 行，并返回拼接后的字符串。"""
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[-n:]) if lines else "(暂无日志)\n"
    except FileNotFoundError:
        return "(日志文件未找到)\n"


def build_interface() -> gr.Blocks:
    """构建并返回 Gradio Blocks 界面。"""
    # 内联 CSS：限制页面最大宽度并水平居中
    custom_css = """
    .gradio-container { width: 1200px; max-width: 1200px; margin: 0 auto; }
    """
    with gr.Blocks(title="UptimeGuard", css=custom_css) as demo:
        gr.Markdown("""
        # UptimeGuard
        仅用 Python + Gradio 的简单网站在线状态监控示例。下方展示站点列表与日志信息。
        """)

        with gr.Column():
            with gr.Column(scale=3):
                gr.Markdown("## 网站列表")

                table = gr.Dataframe(
                    headers=["名称", "URL", "HTTP", "关键字", "SSL", "状态", "失败", "延迟(ms)", "检测时间"],
                    value=_sites_to_table_rows(load_sites()),
                    datatype=["str", "str", "str", "str", "str", "str", "number", "number", "str"],
                    row_count=(0, "dynamic"),
                    interactive=False,
                    wrap=False,
                    label="当前被监控网站"
                )

            with gr.Column(scale=2):
                gr.Markdown("## 日志信息")
                log_box = gr.Textbox(
                    value=get_log_manager(LOG_FILE_PATH).get_history_text(200), 
                    lines=20, 
                    interactive=False, 
                    label="最新日志" ,
                    show_copy_button=True,
                    autoscroll=True
                )
                with gr.Row():
                    refresh_logs_btn = gr.Button("刷新日志")

        # 回调：刷新日志（优先显示新增队列，其次显示历史）
        def on_refresh_logs():
            manager = get_log_manager(LOG_FILE_PATH)
            new_text = manager.drain_queue_as_text()
            if new_text:
                return new_text + "\n"
            return manager.get_history_text(200)

        refresh_logs_btn.click(
            fn=on_refresh_logs,
            inputs=[],
            outputs=[log_box]
        )

        # 周期刷新表格以显示最新快照（每 5 秒）
        def refresh_table(cur_sites: List[Dict[str, Any]]):
            return _sites_to_table_rows(load_sites())

        timer = gr.Timer(5)
        timer.tick(fn=refresh_table, inputs=[], outputs=[table])

        # 日志定时刷新（每 2 秒）
        def refresh_logs_auto():
            manager = get_log_manager(LOG_FILE_PATH)
            new_text = manager.drain_queue_as_text()
            if new_text:
                return new_text + "\n"
            return manager.get_history_text(200)

        logs_timer = gr.Timer(2)
        logs_timer.tick(fn=refresh_logs_auto, inputs=[], outputs=[log_box])

    return demo


if __name__ == "__main__":
    demo = build_interface()

    if is_docker_environment():
        server_port = 7863
        print("🐳 检测到 Docker 环境，使用端口: 7863")
    else:
        server_port = 7864
        print("💻 检测到本地环境，使用端口: 7864")

    demo.launch(
            server_name="0.0.0.0",  # 允许外部访问
            server_port=server_port,# 使用不同端口避免冲突
            share=False,            # 不创建公共链接
            debug=True,             # 开启调试模式
            show_error=True,        # 显示错误信息
            quiet=False             # 显示启动信息
        )


