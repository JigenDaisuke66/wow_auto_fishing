"""Centralized user-facing translations."""

LANGUAGES = {"zh_CN": "简体中文", "en_US": "English"}

ZH_CN = {
    "window_title": "钓鱼助手", "subtitle": "基于窗口内图像识别的轻量自动化工具",
    "tab_general": "钓鱼设置", "tab_window": "游戏窗口", "tab_detection": "识别与咬钩", "tab_log": "运行日志",
    "images": "浮漂模板", "image_hint": "建议添加不同光照、角度下的浮漂叶子截图",
    "add_images": "添加图片", "clear_images": "清空图片", "no_images": "尚未添加浮漂模板",
    "fishing_hotkey": "钓鱼快捷键", "bait_hotkey": "鱼饵快捷键（可选）", "duration": "运行时长（小时）",
    "language": "界面语言", "window_title_label": "游戏窗口标题",
    "window_title_hint": "必须与游戏窗口标题一致，可自行修改", "afk_settings": "防挂机设置",
    "afk_key": "防挂机按键", "afk_range": "防挂机间隔（分钟）", "to": "至",
    "confidence": "模板匹配置信度", "mean_difference": "平均差异阈值", "pixel_threshold": "单像素变化阈值",
    "pixel_ratio": "变化像素比例", "confirmation_frames": "连续确认帧数",
    "detection_hint": "需同时满足平均差异和变化像素比例，并持续多帧，能降低水波与光影误触发。",
    "start": "开始运行", "stop": "安全停止", "ready": "准备就绪",
    "image_filter": "图片 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)",
    "save_failed": "⚠ 保存配置失败：{error}", "need_image": "❌ 请先添加至少一张浮漂模板",
    "need_hotkey": "❌ 请填写钓鱼快捷键", "need_window": "❌ 请填写游戏窗口标题",
    "started": "▶ 钓鱼程序已启动", "stopped": "■ 钓鱼程序已停止",
    "stop_requested": "🛑 已请求安全停止，正在结束当前操作…", "afk_pressed": "⏱ 防挂机：按下 {key}",
    "no_template": "❌ 没有可读取的浮漂模板", "window_failed": "❌ 游戏窗口激活失败，请检查窗口标题",
    "use_bait": "🪱 使用鱼饵…", "cast": "🎣 抛竿钓鱼…", "not_caught": "🟡 本轮未确认咬钩，准备重新抛竿",
    "runtime_error": "❌ 运行错误：{error}", "float_found": "🔍 找到浮漂，置信度 {confidence:.2f}",
    "metrics": "📊 差异 {difference:.1f} / 像素比例 {ratio:.1%} / 确认 {current}/{required}",
    "bite_confirmed": "🟢 已确认咬钩，右键收杆", "template_unreadable": "⚠ 无法读取模板：{name}",
}

EN_US = {
    "window_title": "Fishing Assistant", "subtitle": "A lightweight window-based visual recognition tool",
    "tab_general": "Fishing", "tab_window": "Game Window", "tab_detection": "Detection", "tab_log": "Activity Log",
    "images": "Bobber Templates", "image_hint": "Add bobber images captured under different lighting and viewing angles.",
    "add_images": "Add Images", "clear_images": "Clear Images", "no_images": "No bobber templates added",
    "fishing_hotkey": "Fishing hotkey", "bait_hotkey": "Bait hotkey (optional)", "duration": "Duration (hours)",
    "language": "Language", "window_title_label": "Game window title",
    "window_title_hint": "Must exactly match the game window title. You can edit it here.", "afk_settings": "Anti-AFK Settings",
    "afk_key": "Anti-AFK key", "afk_range": "Anti-AFK interval (minutes)", "to": "to",
    "confidence": "Template confidence", "mean_difference": "Mean difference threshold", "pixel_threshold": "Pixel-change threshold",
    "pixel_ratio": "Changed-pixel ratio", "confirmation_frames": "Confirmation frames",
    "detection_hint": "A bite must satisfy both change thresholds for several consecutive frames, reducing false triggers from water and lighting.",
    "start": "Start", "stop": "Stop Safely", "ready": "Ready",
    "image_filter": "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
    "save_failed": "⚠ Could not save settings: {error}", "need_image": "❌ Add at least one bobber template first",
    "need_hotkey": "❌ Enter the fishing hotkey", "need_window": "❌ Enter the game window title",
    "started": "▶ Fishing assistant started", "stopped": "■ Fishing assistant stopped",
    "stop_requested": "🛑 Safe stop requested; finishing the current operation…", "afk_pressed": "⏱ Anti-AFK: pressed {key}",
    "no_template": "❌ No readable bobber templates", "window_failed": "❌ Could not activate the game window; check its title",
    "use_bait": "🪱 Applying bait…", "cast": "🎣 Casting…", "not_caught": "🟡 No bite confirmed; preparing to cast again",
    "runtime_error": "❌ Runtime error: {error}", "float_found": "🔍 Bobber found; confidence {confidence:.2f}",
    "metrics": "📊 Difference {difference:.1f} / changed pixels {ratio:.1%} / confirmation {current}/{required}",
    "bite_confirmed": "🟢 Bite confirmed; right-clicking", "template_unreadable": "⚠ Could not read template: {name}",
}

TRANSLATIONS = {"zh_CN": ZH_CN, "en_US": EN_US}


def text(key: str, language: str = "zh_CN", **values) -> str:
    selected = TRANSLATIONS.get(language, ZH_CN)
    value = selected.get(key, ZH_CN.get(key, key))
    return value.format(**values) if values else value
