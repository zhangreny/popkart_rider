# popkart_rider

这是一个跑跑卡丁车客户端的小工具仓库。

目前主要内容是“剪刀石头布”活动自动化：用于自动完成游戏里的“剪刀石头布”活动。

## 这个工具能做什么

脚本会看游戏画面，然后自动点击。

它会自动完成这些事：

- 找到剪刀石头布活动入口。
- 点击开始挑战。
- 识别对方出的剪刀、石头、布。
- 选择不会输的牌。
- 平局时继续当前阶段。
- 胜利后进入下一阶段。
- 第 5 阶段胜利后点击“否”。
- 点击奖励弹窗里的“确定”。
- 可以循环跑很多轮。

简单说：打开游戏和活动界面后，让脚本帮你重复打剪刀石头布。

## 文件说明

```text
popkart_rider/
  play_caiquan.exe              可直接双击运行的管理员权限版 exe
  source/
    play_caiquan.py              主脚本
    *.png                        图像识别模板
    build_exe.ps1                exe 打包脚本
    automation_assumptions.md    脚本假设和硬编码说明
```

## 运行前准备

进入脚本目录：

```powershell
cd D:\popkart_rider\source
```

如果电脑还没有安装依赖，先执行：

```powershell
py -m pip install --user pillow numpy opencv-python pyautogui pywin32
```

## 跑一轮

```powershell
py .\play_caiquan.py
```

## 循环运行

```powershell
py .\play_caiquan.py --loop --loop-delay 4
```

参数含义：

- `--loop`：开启循环模式，一轮结束后继续下一轮。
- `--loop-delay 4`：每轮结束后等待 4 秒再开始下一轮。

最多跑 10 轮：

```powershell
py .\play_caiquan.py --loop --max-runs 10 --loop-delay 4
```

## 打包成 exe

项目根目录提供了打包脚本：

```powershell
cd D:\popkart_rider\source
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

打包完成后会生成：

```text
D:\popkart_rider\play_caiquan.exe
```

这个 exe 已经配置为管理员权限启动，双击运行时会弹出 UAC 确认。

exe 也支持脚本参数，例如循环运行：

```powershell
D:\popkart_rider\play_caiquan.exe --loop --loop-delay 4
```

停止 exe 循环时，在项目根目录执行：

```powershell
Set-Content -LiteralPath .\stop.loop -Value stop -NoNewline
```

## 停止循环

源码方式运行时，在 `source` 目录执行：

```powershell
Set-Content -LiteralPath .\stop.loop -Value stop -NoNewline
```

脚本会在当前这一轮结束后停止，不再开启下一轮。

## 如果点击失败

如果看到类似错误：

```text
SetCursorPos
Failed to move the mouse cursor
```

通常是因为游戏客户端用了管理员权限运行，但脚本没有管理员权限。

可以用管理员方式启动：

```powershell
Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command',"Set-Location 'D:\popkart_rider\caiquan'; py .\play_caiquan.py"
```

循环版管理员启动：

```powershell
Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-Command',"Set-Location 'D:\popkart_rider\caiquan'; py .\play_caiquan.py --loop --loop-delay 4"
```

## 注意事项

- 这个脚本依赖当前游戏 UI 布局和图标不变。
- 如果游戏窗口标题、显示器 ID、分辨率缩放或活动界面变化，可能需要调整脚本。
- 详细的硬编码和假设说明在 `source/automation_assumptions.md`。
