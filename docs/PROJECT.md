# 项目说明

## 定位

这是一个仅面向 Windows 的桌面图像自动化学习项目。程序激活指定游戏窗口，在窗口客户区内匹配浮漂模板，并根据浮漂区域的视觉变化判断咬钩。

使用自动输入工具可能违反游戏服务条款并导致账号处罚，使用者需自行确认并承担风险。

## 项目结构

```text
wow_auto_fishing/
├─ auto_fishing.py               # 稳定启动入口
├─ fishing_assistant/
│  ├─ config.py                  # 配置模型、兼容加载与保存
│  ├─ texts.py                   # 界面文案，默认简体中文
│  ├─ ui.py                      # PyQt5 界面与交互
│  ├─ vision.py                  # 模板缓存、匹配与变化计算
│  └─ worker.py                  # 自动化状态循环与安全停止
├─ docs/
│  ├─ PROJECT.md                 # 本文件：结构和功能
│  ├─ CHANGELOG.md               # 修改记录
│  └─ OPTIMIZATION.md            # 算法与后续优化建议
├─ requirements.txt              # 源码运行依赖
└─ README.md                     # 用户使用说明
```

## 功能模块

- 界面：模板管理、快捷键、运行时间、游戏窗口、防挂机和检测参数。
- 配置：继续使用 `fishing_assistant_config.json`，并兼容旧版已有字段。
- 识别：模板在工作线程启动时统一读取，搜索仅覆盖游戏客户区。
- 咬钩：高斯降噪后，同时判断平均灰度差、显著变化像素比例和连续帧数。
- 线程：采用 Qt 中断请求和可中断等待，不再强制终止线程。
- 文案：用户可见的固定文字集中于 `texts.py`，当前默认简体中文。

## 运行

```powershell
py -3 -m pip install -r requirements.txt
py -3 auto_fishing.py
```
