import win32gui
import win32con
import time
import sys
import cv2
import numpy as np
import pyautogui
import json
import os
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, 
                            QSpinBox, QDoubleSpinBox, QFileDialog, QGroupBox, 
                            QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

CONFIG_FILE = "fishing_assistant_config.json"

class FishingAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("钓鱼助手")
        #self.setWindowIcon(QIcon("fishing_icon.png"))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 初始化变量
        self.image_paths = []
        self.fishing_hotkey = ""
        self.bait_hotkey = ""
        self.duration_hours = 2
        self.difference_threshold = 40
        self.running = False
        self.worker_thread = None
        self.confidence_threshold = 0.7  # 图像匹配置信度阈值
        self.game_window_title = "魔兽世界"  # 游戏窗口标题
        self.afk_time_min = 10  # 防AFK时间最小值(分钟)
        self.afk_time_max = 15  # 防AFK时间最大值(分钟)
        self.afk_key = "space"  # 防AFK按键
        
        # 加载配置
        self.load_config()
        
        # 创建主界面
        self.init_ui()
        
        # 设置窗口大小
        self.resize(600, 900)
        
    def init_ui(self):
        # 主窗口布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 1. 图像选择部分
        image_group = QGroupBox("目标图像设置")
        image_layout = QVBoxLayout()
        
        self.image_list = QTextEdit()
        self.image_list.setReadOnly(True)
        self.image_list.setMaximumHeight(100)
        
        add_image_btn = QPushButton("添加图像")
        add_image_btn.clicked.connect(self.add_image)
        remove_image_btn = QPushButton("清除所有图像")
        remove_image_btn.clicked.connect(self.clear_images)
        refresh_images_btn = QPushButton("刷新图像列表")
        refresh_images_btn.clicked.connect(self.update_image_list)
        
        image_btn_layout = QHBoxLayout()
        image_btn_layout.addWidget(add_image_btn)
        image_btn_layout.addWidget(remove_image_btn)
        image_btn_layout.addWidget(refresh_images_btn)
        
        image_layout.addWidget(QLabel("目标图像列表:"))
        image_layout.addWidget(self.image_list)
        image_layout.addLayout(image_btn_layout)
        image_group.setLayout(image_layout)
        
        # 2. 参数设置部分
        param_group = QGroupBox("参数设置")
        param_layout = QVBoxLayout()
        
        # 游戏窗口标题
        game_window_layout = QHBoxLayout()
        game_window_layout.addWidget(QLabel("游戏窗口标题:"))
        self.game_window_input = QLineEdit(self.game_window_title)
        game_window_layout.addWidget(self.game_window_input)
        param_layout.addLayout(game_window_layout)
        
        # 图像差异阈值
        diff_layout = QHBoxLayout()
        diff_layout.addWidget(QLabel("图像差异阈值:"))
        self.diff_spin = QDoubleSpinBox()
        self.diff_spin.setRange(0, 255)
        self.diff_spin.setValue(self.difference_threshold)
        self.diff_spin.setSingleStep(1)
        diff_layout.addWidget(self.diff_spin)
        param_layout.addLayout(diff_layout)
        
        # 图像匹配置信度阈值
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("图像匹配置信度阈值:"))
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 1.0)
        self.confidence_spin.setValue(self.confidence_threshold)
        self.confidence_spin.setSingleStep(0.05)
        confidence_layout.addWidget(self.confidence_spin)
        param_layout.addLayout(confidence_layout)
        
        # 钓鱼快捷键
        fishing_layout = QHBoxLayout()
        fishing_layout.addWidget(QLabel("钓鱼快捷键:"))
        self.fishing_input = QLineEdit(self.fishing_hotkey)
        self.fishing_input.setPlaceholderText("例如: F")
        fishing_layout.addWidget(self.fishing_input)
        param_layout.addLayout(fishing_layout)
        
        # 鱼饵快捷键
        bait_layout = QHBoxLayout()
        bait_layout.addWidget(QLabel("鱼饵快捷键 (可选):"))
        self.bait_input = QLineEdit(self.bait_hotkey)
        self.bait_input.setPlaceholderText("例如: 1")
        bait_layout.addWidget(self.bait_input)
        param_layout.addLayout(bait_layout)
        
        # 持续时间
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("持续时间 (小时):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 24)
        self.duration_spin.setValue(self.duration_hours)
        duration_layout.addWidget(self.duration_spin)
        param_layout.addLayout(duration_layout)
        
        # 防AFK设置
        afk_group = QGroupBox("防AFK设置")
        afk_layout = QVBoxLayout()
        
        # 防AFK按键
        afk_key_layout = QHBoxLayout()
        afk_key_layout.addWidget(QLabel("防AFK按键:"))
        self.afk_key_input = QLineEdit(self.afk_key)
        afk_key_layout.addWidget(self.afk_key_input)
        afk_layout.addLayout(afk_key_layout)
        
        # 防AFK时间范围
        afk_time_layout = QHBoxLayout()
        afk_time_layout.addWidget(QLabel("防AFK时间 (分钟):"))
        
        self.afk_min_spin = QSpinBox()
        self.afk_min_spin.setRange(1, 60)
        self.afk_min_spin.setValue(self.afk_time_min)
        afk_time_layout.addWidget(self.afk_min_spin)
        
        afk_time_layout.addWidget(QLabel("到"))
        
        self.afk_max_spin = QSpinBox()
        self.afk_max_spin.setRange(1, 60)
        self.afk_max_spin.setValue(self.afk_time_max)
        afk_time_layout.addWidget(self.afk_max_spin)
        
        afk_layout.addLayout(afk_time_layout)
        afk_group.setLayout(afk_layout)
        param_layout.addWidget(afk_group)
        
        param_group.setLayout(param_layout)
        
        # 3. 控制按钮部分
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始")
        self.start_btn.clicked.connect(self.start_fishing)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_fishing)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        
        # 4. 日志输出部分
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(200)
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        
        # 将所有部分添加到主布局
        scroll_layout.addWidget(image_group)
        scroll_layout.addWidget(param_group)
        scroll_layout.addLayout(control_layout)
        scroll_layout.addWidget(log_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
        
    def add_image(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择目标图像", "", "Images (*.png *.jpg *.bmp);;All Files (*)", options=options)
        
        if files:
            self.image_paths.extend(files)
            self.update_image_list()
            self.log(f"添加了 {len(files)} 张图像")
            self.save_config()
    
    def clear_images(self):
        self.image_paths = []
        self.update_image_list()
        self.log("已清除所有图像")
        self.save_config()
    
    def update_image_list(self):
        self.image_list.clear()
        if self.image_paths:
            file_names = [os.path.basename(path) for path in self.image_paths]
            self.image_list.setText("\n".join(file_names))
        else:
            self.image_list.setText("没有添加图像")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_output.append(f"[{timestamp}] {message}")
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())
    
    def start_fishing(self):
        if not self.image_paths:
            self.log("错误: 请先添加至少一张目标图像")
            return
            
        if not self.fishing_input.text().strip():
            self.log("错误: 请输入钓鱼快捷键")
            return
            
        self.fishing_hotkey = self.fishing_input.text().strip()
        self.bait_hotkey = self.bait_input.text().strip()
        self.duration_hours = self.duration_spin.value()
        self.difference_threshold = self.diff_spin.value()
        self.confidence_threshold = self.confidence_spin.value()
        self.game_window_title = self.game_window_input.text().strip()
        self.afk_key = self.afk_key_input.text().strip()
        self.afk_time_min = self.afk_min_spin.value()
        self.afk_time_max = self.afk_max_spin.value()
        
        self.save_config()
        
        self.log("开始钓鱼程序...")
        self.log(f"参数设置: 持续时间={self.duration_hours}小时, 图像差异阈值={self.difference_threshold}")
        self.log(f"图像匹配置信度阈值: {self.confidence_threshold}")
        self.log(f"游戏窗口标题: {self.game_window_title}")
        self.log(f"钓鱼快捷键: {self.fishing_hotkey}")
        if self.bait_hotkey:
            self.log(f"鱼饵快捷键: {self.bait_hotkey}")
        self.log(f"防AFK设置: 按键={self.afk_key}, 时间间隔={self.afk_time_min}-{self.afk_time_max}分钟")
        
        self.running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.worker_thread = FishingThread(
            self.image_paths,
            self.fishing_hotkey,
            self.bait_hotkey,
            self.duration_hours,
            self.difference_threshold,
            self.confidence_threshold,
            self.game_window_title,
            self.afk_time_min,
            self.afk_time_max,
            self.afk_key,
            self
        )
        self.worker_thread.log_signal.connect(self.log)
        self.worker_thread.finished.connect(self.on_thread_finished)
        self.worker_thread.start()
    
    def stop_fishing(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.log("正在停止钓鱼程序...")
            self.running = False
            self.worker_thread.stop()
            QTimer.singleShot(5000, self.check_thread_stop)
        else:
            self.on_thread_finished()
    
    def check_thread_stop(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.log("警告: 线程未正常停止，强制终止...")
            self.worker_thread.terminate()
            self.on_thread_finished()
    
    def on_thread_finished(self):
        self.log("钓鱼程序已停止")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.worker_thread = None
    
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.image_paths = config.get('image_paths', [])
                    self.fishing_hotkey = config.get('fishing_hotkey', '')
                    self.bait_hotkey = config.get('bait_hotkey', '')
                    self.duration_hours = config.get('duration_hours', 2)
                    self.difference_threshold = config.get('difference_threshold', 40)
                    self.confidence_threshold = config.get('confidence_threshold', 0.7)
                    self.game_window_title = config.get('game_window_title', '魔兽世界')
                    self.afk_time_min = config.get('afk_time_min', 10)
                    self.afk_time_max = config.get('afk_time_max', 15)
                    self.afk_key = config.get('afk_key', 'space')
                    
                    self.update_image_list()
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_config(self):
        try:
            config = {
                'image_paths': self.image_paths,
                'fishing_hotkey': self.fishing_hotkey,
                'bait_hotkey': self.bait_hotkey,
                'duration_hours': self.duration_hours,
                'difference_threshold': self.difference_threshold,
                'confidence_threshold': self.confidence_threshold,
                'game_window_title': self.game_window_title,
                'afk_time_min': self.afk_time_min,
                'afk_time_max': self.afk_time_max,
                'afk_key': self.afk_key
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            self.stop_fishing()
            event.ignore()
        else:
            self.save_config()


class FishingThread(QThread):
    log_signal = pyqtSignal(str)
    
    def __init__(self, image_paths, fishing_hotkey, bait_hotkey, duration_hours, 
                 difference_threshold, confidence_threshold, game_window_title,
                 afk_time_min, afk_time_max, afk_key, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.fishing_hotkey = fishing_hotkey
        self.bait_hotkey = bait_hotkey
        self.duration_hours = duration_hours
        self.difference_threshold = difference_threshold
        self.confidence_threshold = confidence_threshold
        self.game_window_title = game_window_title
        self.afk_time_min = afk_time_min
        self.afk_time_max = afk_time_max
        self.afk_key = afk_key
        self._running = True

    def run(self):
        last_bait_time = 0
        last_afk_time = 0
        end_time = time.time() + self.duration_hours * 3600
        
        while self._running and time.time() < end_time:
            try:
                current_time = time.time()
                
                if not self.activate_game_window():
                    self.log_signal.emit("❌ 游戏窗口激活失败，请检查窗口标题！")
                    time.sleep(5)
                    continue
                
                # 使用鱼饵
                if self.bait_hotkey and (current_time - last_bait_time >= 660):
                    self.log_signal.emit("🪱 使用鱼饵...")
                    pyautogui.press(self.bait_hotkey)
                    last_bait_time = current_time
                    time.sleep(2)
                
                # 开始钓鱼
                self.log_signal.emit("🎣 抛竿钓鱼...")
                pyautogui.press(self.fishing_hotkey)
                time.sleep(1.5)
                
                # 检测浮漂
                found_float = False
                start_time = time.time()
                
                while time.time() - start_time < 20 and self._running:
                    # 查找浮漂图像
                    found_image, location, img_width, img_height = self.find_float_image()
                    if found_image:
                        self.log_signal.emit(f"🔍 找到浮漂图像: {os.path.basename(found_image)}")
                        
                        # 计算浮漂右下角坐标(向右下方偏移10像素)
                        target_x = location[0] + img_width - 10
                        target_y = location[1] + img_height - 10
                        
                        # 移动鼠标到浮漂右下方
                        pyautogui.moveTo(target_x, target_y, duration=0.3)
                        self.log_signal.emit(f"🖱 鼠标移动到浮漂右下方: ({target_x}, {target_y})")
                        
                        # 获取初始截图(浮漂区域)
                        previous_screenshot = self.get_screen_region(
                            location[0], location[1], 
                            img_width, img_height
                        )
                        
                        # 持续监测图像变化
                        while time.time() - start_time < 20 and self._running:
                            current_screenshot = self.get_screen_region(
                                location[0], location[1],
                                img_width, img_height
                            )
                            
                            if current_screenshot is None:
                                self.log_signal.emit("⚠ 无法获取当前屏幕截图")
                                break
                                
                            difference = self.calculate_image_difference(previous_screenshot, current_screenshot)
                            
                            self.log_signal.emit(f"📊 当前图像差异: {difference:.2f} (阈值: {self.difference_threshold})")
                            
                            if difference > self.difference_threshold:
                                self.log_signal.emit(f"🟢 检测到浮漂变化（差异: {difference:.2f}），右键点击！")
                                pyautogui.click(button='right')
                                found_float = True
                                time.sleep(1)
                                break
                            
                            previous_screenshot = current_screenshot
                            time.sleep(0.1)
                        
                        if found_float:
                            break
                    else:
                        self.log_signal.emit("🔍 未找到浮漂图像，继续搜索...")
                    
                    time.sleep(0.5)
                    
                    # 防AFK - 随机时间间隔内执行
                    if current_time - last_afk_time >= random.randint(self.afk_time_min*60, self.afk_time_max*60):
                        pyautogui.press(self.afk_key)
                        self.log_signal.emit(f"⏱ 防AFK：按键 {self.afk_key} (间隔: {self.afk_time_min}-{self.afk_time_max}分钟)")
                        last_afk_time = current_time
                
                if not found_float and self._running:
                    self.log_signal.emit("🟡 未检测到浮漂，可能已自动上钩或超时")
                time.sleep(3)
            except Exception as e:
                self.log_signal.emit(f"❌ 发生错误: {str(e)}")
                time.sleep(5)

    def find_float_image(self):
        """查找浮漂图像并返回图像路径、位置和尺寸"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            for image_path in self.image_paths:
                target_image = cv2.imread(image_path)
                if target_image is None:
                    self.log_signal.emit(f"⚠ 无法读取图像: {os.path.basename(image_path)}")
                    continue
                result = cv2.matchTemplate(screenshot, target_image, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val >= self.confidence_threshold:
                    # 返回图像路径、位置(x,y)和尺寸(width,height)
                    return (image_path, max_loc, target_image.shape[1], target_image.shape[0])
            return (None, None, 0, 0)
        except Exception as e:
            self.log_signal.emit(f"❌ 图像识别错误: {str(e)}")
            return (None, None, 0, 0)

    def get_screen_region(self, x, y, width, height):
        """获取屏幕指定区域的截图"""
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            self.log_signal.emit(f"❌ 截图错误: {str(e)}")
            return None

    def calculate_image_difference(self, img1, img2):
        """计算两幅图像的差异"""
        try:
            if img1 is None or img2 is None:
                return 0
                
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray1, gray2)
            return np.mean(diff)
        except Exception as e:
            self.log_signal.emit(f"❌ 计算图像差异错误: {str(e)}")
            return 0

    def activate_game_window(self):
        """激活游戏窗口"""
        try:
            hwnd = win32gui.FindWindow(None, self.game_window_title)
            if hwnd:
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)
                return True
            return False
        except Exception as e:
            self.log_signal.emit(f"❌ 激活窗口错误: {str(e)}")
            return False
    
    def stop(self):
        """停止线程运行"""
        self._running = False
        self.log_signal.emit("🛑 正在停止钓鱼线程...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setFamily("Microsoft YaHei")
    app.setFont(font)
    window = FishingAssistant()
    window.show()
    sys.exit(app.exec_())

