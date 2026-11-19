# ClipNest

一款 Windows 本地剪贴板历史工具。自动记录复制的文字，支持搜索、置顶和重新复制，所有数据只保存在你自己的电脑上。

## 功能

- 自动记录复制过的文本，重复内容自动去重并置顶显示
- 实时搜索历史记录
- 置顶重要内容，不会被自动清理
- 删除单条记录、清空未置顶记录
- 暂停 / 恢复剪贴板监听
- 系统托盘常驻，关闭窗口后继续在后台记录
- 数据存入本地 SQLite，关闭程序后依然保留
- 最多保留 500 条未置顶记录，防止无限增长

## 运行

需要 Windows 和 Python 3.9 以上版本。

```powershell
git clone https://github.com/balabalahong99/ClipNest.git
cd ClipNest
python -m pip install -r requirements.txt
python app.py
```

## 使用

1. 启动程序后，在任意软件里复制文字（Ctrl+C）。
2. 内容会以 500 毫秒的间隔被自动记录到列表中。
3. 点击列表中的任意一条，即可把它重新复制回剪贴板。
4. 使用顶部搜索框筛选内容，用 `★` 标记置顶项。
5. 点窗口的 × 会收进系统托盘，双击托盘图标恢复窗口；退出请用托盘菜单里的“退出”。

## 数据存放位置

```text
%LOCALAPPDATA%\ClipNest\history.db
```

这是一个标准 SQLite 数据库文件，可以用任何 SQLite 工具打开查看。程序不会联网，剪贴板内容不会离开本机。

## 项目结构

```text
clipnest/
├── app.py            # 界面、剪贴板监听、托盘与交互逻辑
├── database.py       # SQLite 存取、去重和数量限制
├── requirements.txt  # 运行依赖
├── .gitignore
└── README.md
```

## 打包为 exe

```powershell
python -m pip install -r requirements-dev.txt
pyinstaller --noconfirm --onefile --windowed --name ClipNest --collect-all pystray app.py
```

产物位于 `dist\ClipNest.exe`，可以直接复制到没有 Python 环境的 Windows 电脑上运行。

## 已知限制

- 仅记录纯文本，暂不支持图片和文件
- 暂不支持全局快捷键
- 数据未加密，请勿在公共电脑上长期使用

## 后续计划

- [x] 系统托盘常驻
- [ ] 全局快捷键唤起
- [ ] 支持图片剪贴板
- [ ] 开机自启动
- [ ] 界面主题与字体设置

## 技术栈

Python 3.9 · Tkinter · pystray · SQLite · PyInstaller

## 许可证

[MIT](LICENSE)
