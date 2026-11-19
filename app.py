import tkinter as tk
from tkinter import messagebox, ttk

from database import Database

# 每隔多少毫秒检查一次剪贴板
POLL_INTERVAL_MS = 500


class ClipNestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ClipNest")
        self.root.geometry("760x520")
        self.root.minsize(560, 400)

        self.db = Database()
        self.last_text = ""   # 上一次记录的剪贴板内容，用来去重
        self.items = []       # 当前列表显示的记录，直接来自数据库
        self.paused = False   # 是否暂停监听

        self.build_ui()
        self.refresh()
        self.poll_clipboard()

    def build_ui(self):
        # 顶部搜索栏
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(top, text="搜索", font=("Microsoft YaHei UI", 10)).pack(
            side="left", padx=(0, 8)
        )

        self.keyword = tk.StringVar()
        # 输入框内容一变就重新查询，实现实时搜索
        self.keyword.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(top, textvariable=self.keyword, font=("Microsoft YaHei UI", 10)).pack(
            side="left", fill="x", expand=True
        )

        # 功能按钮
        tools = tk.Frame(self.root)
        tools.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Button(tools, text="置顶 / 取消置顶", command=self.toggle_pin).pack(side="left")
        ttk.Button(tools, text="删除", command=self.delete_selected).pack(side="left", padx=8)
        ttk.Button(tools, text="清空未置顶", command=self.clear_unpinned).pack(side="left")

        self.pause_btn = ttk.Button(tools, text="暂停监听", command=self.toggle_pause)
        self.pause_btn.pack(side="right")

        # 列表 + 滚动条
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=16)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame,
            font=("Microsoft YaHei UI", 11),
            activestyle="none",
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<ButtonRelease-1>", self.on_click)

        self.status = tk.Label(
            self.root,
            text="",
            anchor="w",
            fg="#666666",
            font=("Microsoft YaHei UI", 9),
        )
        self.status.pack(fill="x", padx=16, pady=(8, 12))

    def refresh(self):
        """按当前搜索词从数据库读取数据并重绘列表。"""
        keyword = self.keyword.get().strip()
        self.items = self.db.list_clips(keyword)

        self.listbox.delete(0, tk.END)
        for row in self.items:
            prefix = "★ " if row["pinned"] else ""
            self.listbox.insert(tk.END, prefix + self.preview(row["content"]))

        state = "已暂停" if self.paused else "监听中"
        self.status.config(text=f"{len(self.items)} 条记录 · {state}")

    def poll_clipboard(self):
        """定时读取剪贴板，发现新内容就存进数据库。"""
        if not self.paused:
            text = self.read_clipboard()
            if text and text != self.last_text:
                self.last_text = text
                self.db.add(text)
                self.refresh()
        self.root.after(POLL_INTERVAL_MS, self.poll_clipboard)

    def read_clipboard(self):
        """读取剪贴板文本；剪贴板为空或不是文字时返回空字符串。"""
        try:
            return self.root.clipboard_get()
        except tk.TclError:
            return ""

    @staticmethod
    def preview(text):
        """把多行内容压成一行并截断，方便在列表里查看。"""
        one_line = " ".join(text.split())
        return one_line[:80] + ("…" if len(one_line) > 80 else "")

    def selected_row(self):
        """返回当前选中的那条记录，没有选中时返回 None。"""
        selection = self.listbox.curselection()
        if not selection:
            return None
        return self.items[selection[0]]

    def on_click(self, event):
        """点击列表项时，把对应内容重新复制到剪贴板。"""
        index = self.listbox.nearest(event.y)
        if index < 0 or index >= len(self.items):
            return

        # nearest 会返回最近的行，点击空白区域时要排除
        bbox = self.listbox.bbox(index)
        if not bbox or not (bbox[1] <= event.y <= bbox[1] + bbox[3]):
            return

        text = self.items[index]["content"]
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.last_text = text  # 避免自己复制的内容又被记录一次
        self.status.config(text="已复制回剪贴板")

    def toggle_pin(self):
        row = self.selected_row()
        if row is None:
            self.status.config(text="请先在列表里选中一条记录")
            return
        self.db.set_pinned(row["id"], not row["pinned"])
        self.refresh()

    def delete_selected(self):
        row = self.selected_row()
        if row is None:
            self.status.config(text="请先在列表里选中一条记录")
            return
        self.db.delete(row["id"])
        self.refresh()

    def clear_unpinned(self):
        if not messagebox.askyesno("确认", "清空所有未置顶的记录？置顶内容会保留。"):
            return
        self.db.clear_unpinned()
        self.refresh()

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.config(text="恢复监听" if self.paused else "暂停监听")
        self.refresh()


def main():
    root = tk.Tk()
    app = ClipNestApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.db.close(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
