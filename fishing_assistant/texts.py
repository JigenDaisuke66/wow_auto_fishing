"""User-facing text. Add another mapping to introduce a new language."""

ZH_CN = {
    "window_title": "钓鱼助手",
    "subtitle": "基于窗口内图像识别的轻量自动化工具",
    "tab_general": "钓鱼设置",
    "tab_window": "游戏窗口",
    "tab_detection": "识别与咬钩",
    "tab_log": "运行日志",
    "images": "浮漂模板",
    "image_hint": "建议添加不同光照、角度下的浮漂叶子截图",
    "add_images": "添加图片",
    "clear_images": "清空图片",
    "no_images": "尚未添加浮漂模板",
    "fishing_hotkey": "钓鱼快捷键",
    "bait_hotkey": "鱼饵快捷键（可选）",
    "duration": "运行时长（小时）",
    "window_title_label": "游戏窗口标题",
    "window_title_hint": "必须与游戏窗口标题一致，可自行修改",
    "afk_settings": "防挂机设置",
    "afk_key": "防挂机按键",
    "afk_range": "防挂机间隔（分钟）",
    "to": "至",
    "confidence": "模板匹配置信度",
    "mean_difference": "平均差异阈值",
    "pixel_threshold": "单像素变化阈值",
    "pixel_ratio": "变化像素比例",
    "confirmation_frames": "连续确认帧数",
    "detection_hint": "需同时满足平均差异和变化像素比例，并持续多帧，能降低水波与光影误触发。",
    "start": "开始运行",
    "stop": "安全停止",
    "ready": "准备就绪",
}


def text(key: str, language: str = "zh_CN") -> str:
    # The argument is intentionally retained as the future language switch seam.
    return ZH_CN.get(key, key)
