# 剪刀石头布工具说明

这是跑跑卡丁车“剪刀石头布”活动的自动化工具。

## 直接运行

先打开游戏，并进入“剪刀石头布”活动页面。

然后双击运行：

```text
play_caiquan.exe
```

默认会一直循环，直到下方剪刀、石头、布任意一种数量变成 `X 0`。

如果弹出管理员权限确认，点“是”。

## 常用参数

只跑一轮：

```powershell
.\play_caiquan.exe --once
```

每轮之间等待 4 秒：

```powershell
.\play_caiquan.exe --loop-delay 4
```

最多跑 10 轮：

```powershell
.\play_caiquan.exe --max-runs 10
```

手动停止循环：

```powershell
Set-Content -LiteralPath .\stop.loop -Value stop -NoNewline
```

工具会跑完当前这一轮后停止。

## 文件

```text
剪刀石头布/
  play_caiquan.exe          可直接运行的工具
  README.md                 本说明
  source/
    play_caiquan.py         主脚本
    build_exe.ps1           打包脚本
    *.png                   图像识别模板
    automation_assumptions.md
```

## 源码运行

进入源码目录：

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

只跑一轮：

```powershell
py .\play_caiquan.py --once
```

## 重新打包

修改源码或图片模板后执行：

```powershell
cd D:\popkart_rider\剪刀石头布\source
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

打包完成后会覆盖：

```text
D:\popkart_rider\剪刀石头布\play_caiquan.exe
```

## 注意

- 游戏如果用管理员权限运行，工具也需要管理员权限。
- 如果识别不到按钮或图标，通常是活动 UI 或图片模板变了。
- 如果一启动就停止，检查 `stop.loop` 是否还存在。
