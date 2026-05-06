# 跑跑卡丁车活动小工具

这里会放一些跑跑卡丁车活动用的小工具。每个活动一个文件夹，里面一般会有：

- 一个可以直接双击运行的 `exe`
- 一份源码
- 重新打包 `exe` 的脚本
- 自动识别用的图片模板

目前已有工具：**剪刀石头布**。

## 现在要用哪个？

如果你只是想直接使用，打开这个文件：

```text
剪刀石头布/play_caiquan.exe
```

双击运行即可。

第一次运行时 Windows 可能会弹出管理员权限确认，这是正常的。游戏如果是管理员权限运行，小工具也必须用管理员权限才能点击游戏窗口。

## 剪刀石头布怎么用？

1. 先打开跑跑卡丁车客户端。
2. 进入“剪刀石头布”活动页面。
3. 双击运行 `剪刀石头布/play_caiquan.exe`。
4. 让它自动完成活动流程。

如果想循环跑很多轮，可以在 PowerShell 里执行：

```powershell
cd D:\popkart_rider\剪刀石头布
.\play_caiquan.exe --loop --loop-delay 4
```

如果只想最多跑 10 轮：

```powershell
cd D:\popkart_rider\剪刀石头布
.\play_caiquan.exe --loop --max-runs 10 --loop-delay 4
```

## 怎么停止循环？

在另一个 PowerShell 窗口里执行：

```powershell
cd D:\popkart_rider\剪刀石头布
Set-Content -LiteralPath .\stop.loop -Value stop -NoNewline
```

它不会立刻强行中断当前操作，而是会在当前这一轮结束后停止。

如果下次还要循环运行，记得删除 `stop.loop` 文件。

## 想改源码怎么办？

源码在这里：

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

运行源码：

```powershell
py .\play_caiquan.py
```

循环运行源码：

```powershell
py .\play_caiquan.py --loop --loop-delay 4
```

## 改完源码后怎么重新打包 exe？

进入源码目录：

```powershell
cd D:\popkart_rider\剪刀石头布\source
```

执行打包脚本：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
```

打包完成后，会生成新的：

```text
剪刀石头布/play_caiquan.exe
```

这个文件会覆盖旧的 exe。

## 常用参数

| 参数 | 用途 |
| --- | --- |
| `--loop` | 一轮结束后继续跑下一轮 |
| `--max-runs 10` | 最多跑 10 轮，不写就是不限制 |
| `--loop-delay 4` | 每轮之间等 4 秒 |

## 文件夹说明

```text
popkart_rider/
  README.md
  剪刀石头布/
    play_caiquan.exe
    source/
      play_caiquan.py
      build_exe.ps1
      *.png
      automation_assumptions.md
```

以后如果有其他活动，会继续新增类似这样的文件夹，例如：

```text
活动名称/
  活动工具.exe
  source/
    活动源码.py
    build_exe.ps1
    图片模板.png
```

## 出问题先看这里

- 点不动游戏：大概率是权限问题。游戏用管理员权限运行时，小工具也要管理员权限。
- 识别不到按钮或图标：可能是游戏 UI 更新、窗口缩放变化，或者活动页面没有打开到正确位置。
- 循环刚启动就停了：检查目录里是不是已经有 `stop.loop` 文件。
- 改了源码但 exe 没变化：需要重新打包 exe。

剪刀石头布更细的自动化假设在：

```text
剪刀石头布/source/automation_assumptions.md
```
