"""
app.py

应用入口：启动监控后台线程并启动 Gradio 界面。
"""

from ui import build_interface
from storage import load_sites
from monitor import start_background_polling


def main():
    # 启动后台轮询（模拟监控），默认 30s 一次
    start_background_polling(load_sites, interval_seconds=15)

    # 启动 UI
    demo = build_interface()
    # share=True 便于远程演示，可按需关闭
    demo.launch()


if __name__ == "__main__":
    main()


