# 跑跑卡丁车剪刀石头布工具

这是跑跑卡丁车“剪刀石头布”活动的自动化小工具。

打开游戏并进入“剪刀石头布”活动页面后，双击运行：

```text
剪刀石头布/play_caiquan.exe
```

如果弹出管理员权限确认，点“是”。

## 自动流程

工具会自动：

- 找到游戏窗口所在显示器。
- 进入剪刀石头布活动。
- 点击开始挑战。
- 识别对方出牌。
- 选择不会输的牌。
- 打到第 5 阶段胜利后点击“否”。
- 点击奖励确认。
- 自动开始下一轮。

默认会一直循环，直到下方剪刀、石头、布任意一种数量变成 `X 0`。

## 常用参数

```powershell
cd D:\popkart_rider\剪刀石头布
```

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

## 源码和打包

源码在：

```text
剪刀石头布/source/play_caiquan.py
```

修改源码或图片模板后，重新打包：

```powershell
cd D:\popkart_rider\剪刀石头布\source
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

打包后会覆盖：

```text
剪刀石头布/play_caiquan.exe
```

## 注意

- 游戏如果用管理员权限运行，工具也需要管理员权限。
- 如果识别不到按钮或图标，通常是活动 UI 或图片模板变了。
- 如果一启动就停止，检查 `剪刀石头布/stop.loop` 是否还存在。
