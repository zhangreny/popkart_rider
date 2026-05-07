# 跑跑卡丁车剪刀石头布工具

打开游戏并进入“剪刀石头布”活动页面后，双击运行：

```text
剪刀石头布/play_caiquan.exe
```

如果弹出管理员权限确认，点“是”。

默认会一直循环，直到下方剪刀、石头、布任意一种数量变成 `X 0`。

## 参数

进入 exe 目录：

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

## 注意

- 游戏如果用管理员权限运行，工具也需要管理员权限。
- 如果一启动就停止，检查 `剪刀石头布/stop.loop` 是否还存在。
