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
from telegram_config import load_config, is_telegram_configured
from telegram_notifier import test_telegram_connection
from telegram_chat_bot import start_chat_bot, test_chat_bot


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
        ⚡ 实时监控 | 智能告警 | 简单易用 - 让网站监控变得简单 [GitHub 源码](https://github.com/zq535228/UptimeGuard)
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
                    refresh_logs_btn = gr.Button("🔄 刷新日志")
                    cleanup_logs_btn = gr.Button("🧹 清理旧日志", variant="secondary")
                cleanup_status = gr.Textbox(
                    value="",
                    label="清理状态",
                    interactive=False,
                    visible=False
                )

        # Telegram 配置区域
        with gr.Accordion("🔔 Telegram 通知配置", open=False):
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### 配置参数")
                    
                    # 加载当前配置
                    current_config = load_config()
                    
                    telegram_enabled = gr.Checkbox(
                        label="启用 Telegram 通知",
                        value=current_config["enabled"],
                        interactive=False,
                        info="只读：通过配置文件修改"
                    )
                    
                    bot_token = gr.Textbox(
                        label="Bot Token",
                        value=current_config["bot_token"],
                        type="password",
                        interactive=False,
                        placeholder="通过配置文件设置",
                        info="只读：通过配置文件修改"
                    )
                    
                    chat_id = gr.Textbox(
                        label="Chat ID",
                        value=current_config["chat_id"],
                        interactive=False,
                        placeholder="通过配置文件设置",
                        info="只读：通过配置文件修改"
                    )
                    
                    failure_threshold = gr.Number(
                        label="连续失败阈值",
                        value=current_config["failure_threshold"],
                        minimum=1,
                        maximum=100,
                        step=1,
                        interactive=False,
                        info="只读：通过配置文件修改"
                    )
                    
                    with gr.Row():
                        test_connection_btn = gr.Button("🧪 测试连接")
                        reset_config_btn = gr.Button("🔄 重置配置")
                    
                    with gr.Row():
                        start_chat_bot_btn = gr.Button("🤖 启动聊天机器人", variant="secondary")
                        test_chat_bot_btn = gr.Button("🧪 测试聊天机器人")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 配置说明")
                    gr.Markdown("""
                    **⚠️ 重要提示：**
                    配置参数为只读模式，只能通过以下方式修改：
                    
                    **1. 直接编辑配置文件：**
                    - 文件路径：`docker-compose.yml`
                    - 修改后重启应用即可生效
                    
                    **2. 环境变量配置：**
                    - `TELEGRAM_BOT_TOKEN`
                    - `TELEGRAM_CHAT_ID`
                    - `TELEGRAM_ENABLED=true`
                    - `TELEGRAM_FAILURE_THRESHOLD=10`
                    
                    **如何获取 Bot Token:**
                    1. 在 Telegram 中搜索 @BotFather
                    2. 发送 `/newbot` 命令
                    3. 按提示创建机器人
                    4. 复制获得的 Token
                    
                    **如何获取 Chat ID:**
                    **方法一（推荐）:** 使用聊天机器人
                    1. 点击 "🤖 启动聊天机器人" 按钮
                    2. 向机器人发送任意消息（如"你好"）
                    3. Chat ID 会自动获取并保存到配置文件`docker-compose.yml`
                    
                    **方法二（手动）:** 通过 API
                    1. 将机器人添加到群组或私聊
                    2. 发送任意消息给机器人
                    3. 访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
                    4. 在返回的 JSON 中找到 chat.id
                    """)
                    
                    config_status = gr.Textbox(
                        label="配置状态",
                        value="✅ 配置正常" if is_telegram_configured() else "❌ 未配置或配置不完整",
                        interactive=False,
                        lines=2
                    )
                    

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

        # 回调：清理旧日志
        def on_cleanup_logs():
            manager = get_log_manager(LOG_FILE_PATH)
            result = manager.cleanup_logs_now()
            # 清理后刷新日志显示
            return manager.get_history_text(200), result

        cleanup_logs_btn.click(
            fn=on_cleanup_logs,
            inputs=[],
            outputs=[log_box, cleanup_status]
        )

        # Telegram 配置回调函数
        def test_telegram_config(enabled, token, chat_id, threshold):
            """测试 Telegram 连接"""
            # 注意：由于配置现在只能通过环境变量设置，
            # 这里只能测试当前环境变量中的配置
            config = load_config()
            
            if not config.get("enabled"):
                return "⚠️ 请先通过环境变量设置 TELEGRAM_ENABLED=true"
            if not config.get("bot_token") or not config.get("chat_id"):
                return "❌ 请先通过环境变量设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID"
            
            try:
                if test_telegram_connection():
                    return "✅ 测试成功！已收到测试消息"
                else:
                    return "❌ 测试失败，请检查配置"
            except Exception as e:
                return f"❌ 测试异常: {str(e)}"

        def reset_telegram_config():
            """重置 Telegram 配置"""
            # 注意：由于配置现在只能通过环境变量设置，
            # 重置功能已不可用，只能显示当前配置状态
            config = load_config()
            return (
                config.get("enabled", False),
                config.get("bot_token", ""),
                config.get("chat_id", ""),
                config.get("failure_threshold", 10),
                "⚠️ 配置现在只能通过环境变量设置，无法在界面中重置"
            )

        # 绑定回调函数
        test_connection_btn.click(
            fn=test_telegram_config,
            inputs=[telegram_enabled, bot_token, chat_id, failure_threshold],
            outputs=[config_status]
        )

        reset_config_btn.click(
            fn=reset_telegram_config,
            inputs=[],
            outputs=[telegram_enabled, bot_token, chat_id, failure_threshold, config_status]
        )

        # 聊天机器人回调函数
        def start_chat_bot_ui():
            """启动聊天机器人并返回状态信息"""
            try:
                # 检查是否已配置 Bot Token
                config = load_config()
                if not config.get("bot_token"):
                    return "❌ 请先配置 Bot Token"
                
                # 启动聊天机器人（在后台线程中运行）
                import threading
                def run_chat_bot():
                    start_chat_bot()
                
                thread = threading.Thread(target=run_chat_bot, daemon=True)
                thread.start()
                
                return "🤖 聊天机器人已启动！请向机器人发送消息获取 Chat ID"
            except Exception as e:
                return f"❌ 启动聊天机器人失败: {str(e)}"

        def test_chat_bot_ui():
            """测试聊天机器人功能"""
            try:
                if test_chat_bot():
                    return "✅ 聊天机器人测试成功！"
                else:
                    return "❌ 聊天机器人测试失败，请检查配置"
            except Exception as e:
                return f"❌ 测试异常: {str(e)}"

        # 绑定聊天机器人按钮
        start_chat_bot_btn.click(
            fn=start_chat_bot_ui,
            inputs=[],
            outputs=[config_status]
        )

        test_chat_bot_btn.click(
            fn=test_chat_bot_ui,
            inputs=[],
            outputs=[config_status]
        )
        

        # 周期刷新表格以显示最新快照（每 5 秒）
        def refresh_table():
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


