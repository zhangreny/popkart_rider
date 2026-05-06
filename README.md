# popkart_rider

这个仓库目前包含一个 `caiquan` 自动化脚本，用于跑跑卡丁车客户端里的“剪刀石头布”活动。

## caiquan 是什么

`caiquan` 目录里保存了活动自动化所需的 Python 脚本和图像模板。脚本会通过屏幕截图和模板匹配识别游戏界面元素，再模拟鼠标点击完成活动流程。

它主要处理这些步骤：

- 点击活动入口。
- 点击开始挑战确认。
- 识别对方剪刀、石头、布。
- 自动选择不会输的手牌。
- 根据右侧阶段列表判断当前阶段。
- 平局时继续当前阶段。
- 第 5 阶段胜利后点击“否”，再点击奖励弹窗里的“确定”。
- 支持循环执行多轮。

## 目录内容

- `caiquan/play_caiquan.py`：主自动化脚本。
- `caiquan/*.png`：图像识别模板。
- `caiquan/automation_assumptions.md`：脚本假设、硬编码项和运行说明。

## 基本运行

进入 `caiquan` 目录后执行：

```powershell
py .\play_caiquan.py
```

循环执行：

```powershell
py .\play_caiquan.py --loop --loop-delay 4
```

停止循环：

```powershell
Set-Content -LiteralPath .\stop.loop -Value stop -NoNewline
```

## 注意事项

- 脚本依赖当前 UI 布局和模板图片保持不变。
- 如果游戏客户端以管理员权限运行，脚本也需要以管理员权限运行才能点击。
- 当前目标显示器 ID、窗口标题、识别区域比例等细节见 `caiquan/automation_assumptions.md`。
