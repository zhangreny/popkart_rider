# 剪刀石头布源码说明

这里是“剪刀石头布”活动自动化工具的源码目录。

## 文件

```text
source/
  play_caiquan.py              主脚本
  build_exe.ps1                打包脚本
  *.png                        图像识别模板
  automation_assumptions.md    固定假设和可调参数说明
```

## 源码运行

进入目录：

```powershell
cd D:\popkart_rider\剪刀石头布\source
```

安装依赖：

```powershell
py -m pip install --user pillow numpy opencv-python pyautogui pywin32
```

运行：

```powershell
py .\play_caiquan.py
```

默认会一直循环，直到下方剪刀、石头、布任意一种数量变成 `X 0`。

只跑一轮：

```powershell
py .\play_caiquan.py --once
```

## 打包 exe

修改源码或图片模板后执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

打包完成后会覆盖：

```text
D:\popkart_rider\剪刀石头布\play_caiquan.exe
```

## 运行逻辑

脚本会自动检测 `PopKart Client` 窗口所在显示器，然后截图识别活动界面。

每轮流程：

- 进入活动并点击开始。
- 识别当前阶段。
- 识别对方出牌。
- 点击自己的可用牌。
- 处理结果弹窗。
- 第 5 阶段胜利后领取奖励。
- 下一轮开始前检查底部牌数。

如果任意一种牌数为 `X 0`，脚本停止。
