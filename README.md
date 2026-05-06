# 使用指南

这个仓库目前包含跑跑卡丁车“剪刀石头布”活动的小工具。

如果以后增加其他活动，也会按活动单独放到不同文件夹里。

## 1. 直接运行

先打开游戏，并进入“剪刀石头布”活动页面。

然后双击运行：

```text
剪刀石头布/play_caiquan.exe
```

如果 Windows 弹出管理员权限确认，点“是”。

如果游戏本身是用管理员权限打开的，这个工具也必须用管理员权限运行，否则可能点不动游戏窗口。

## 2. 循环运行

如果想连续跑多轮，在 PowerShell 里执行：

```powershell
cd D:\popkart_rider\剪刀石头布
.\play_caiquan.exe --loop --loop-delay 4
```

最多跑 10 轮：

```powershell
cd D:\popkart_rider\剪刀石头布
.\play_caiquan.exe --loop --max-runs 10 --loop-delay 4
```

停止循环：

```powershell
cd D:\popkart_rider\剪刀石头布
Set-Content -LiteralPath .\stop.loop -Value stop -NoNewline
```

工具会跑完当前这一轮再停止。

下次还要循环运行前，记得删除：

```text
剪刀石头布/stop.loop
```

## 3. 参数说明

| 参数 | 说明 |
| --- | --- |
| `--loop` | 一轮结束后继续跑下一轮 |
| `--loop-delay 4` | 每轮之间等待 4 秒 |
| `--max-runs 10` | 最多跑 10 轮，不写就是不限制 |

## 4. 使用源码运行

源码在：

```text
剪刀石头布/source/play_caiquan.py
```

进入源码目录：

```powershell
cd D:\popkart_rider\剪刀石头布\source
```

安装依赖：

```powershell
py -m pip install --user pillow numpy opencv-python pyautogui pywin32
```

运行一轮：

```powershell
py .\play_caiquan.py
```

循环运行：

```powershell
py .\play_caiquan.py --loop --loop-delay 4
```

## 5. 重新打包 exe

如果修改了源码或图片模板，需要重新打包 exe。

进入源码目录：

```powershell
cd D:\popkart_rider\剪刀石头布\source
```

执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

打包完成后会生成并覆盖：

```text
剪刀石头布/play_caiquan.exe
```

## 6. 文件说明

```text
剪刀石头布/
  play_caiquan.exe          直接运行的工具
  source/
    play_caiquan.py         源码
    build_exe.ps1           打包脚本
    *.png                   图片识别模板
    automation_assumptions.md
```

以后新增其他活动时，也会尽量保持类似结构：

```text
活动名称/
  活动工具.exe
  source/
    源码.py
    build_exe.ps1
    图片模板.png
```

## 7. 常见问题

如果工具点不动游戏：

检查游戏和工具是不是权限一致。游戏用管理员权限运行时，工具也要用管理员权限运行。

如果识别不到按钮或图标：

先确认已经进入正确活动页面。如果游戏更新过，可能需要重新截取 `source` 里的图片模板，或者调整源码逻辑。

如果循环一开始就停止：

检查 `剪刀石头布/stop.loop` 是否存在，存在就删掉。
