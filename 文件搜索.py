"""
    Author: Israel Dryer
    Modified: 2021-12-12
    Adapted from: https://github.com/israel-dryer/File-Search-Engine-Tk
    打包 128x128 ico： pyinstaller 文件搜索.py -i search.ico -F -w --collect-all ttkbootstrap
"""
import datetime
import pathlib
from queue import Queue
from threading import Thread
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import utility
from ttkbootstrap.toast import ToastNotification

from util.util import read_file_text, filter_term_in


class FileSearchEngine(ttk.Frame):
    queue = Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        # application variables
        _path = pathlib.Path().absolute().as_posix()
        self.path_var = ttk.StringVar(value=_path)
        self.term_var = ttk.StringVar(value='')
        self.type_var = ttk.StringVar(value='endswidth')
        self.select_box_text = '文件名'

        # header and labelframe option container
        option_text = "输入关键字"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_path_row()
        self.create_term_row()
        self.create_type_row()
        self.create_results_view()

        self.progressbar = ttk.Progressbar(
            master=self,
            mode=INDETERMINATE,
            bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack(fill=X, expand=YES)

    def create_path_row(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="路径", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row,
            text="浏览",
            command=self.on_browse,
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_term_row(self):
        """Add term row to labelframe"""
        term_row = ttk.Frame(self.option_lf)
        term_row.pack(fill=X, expand=YES, pady=15)
        term_lbl = ttk.Label(term_row, text="内容", width=8)
        term_lbl.pack(side=LEFT, padx=(15, 0))
        term_ent = ttk.Entry(term_row, textvariable=self.term_var)
        term_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)

        # 下拉框
        select_box_texts = ['文件名', '文件内容']
        select_box = ttk.Combobox(
            master=term_row,
            text=self.select_box_text,
            values=select_box_texts,
            width=8
        )
        select_box.pack(side=LEFT, padx=5)
        select_box.current(select_box_texts.index(self.select_box_text))

        def change_theme(e):
            self.select_box_text = select_box.get()
        select_box.bind('<<ComboboxSelected>>', change_theme)
        # 下拉框结束

        search_btn = ttk.Button(
            master=term_row,
            text="搜索",
            command=self.on_search,
            bootstyle=INFO,
            width=8
        )
        search_btn.pack(side=LEFT, padx=5)

    def create_type_row(self):
        """Add type row to labelframe"""
        type_row = ttk.Frame(self.option_lf)
        type_row.pack(fill=X, expand=YES)
        type_lbl = ttk.Label(type_row, text="匹配", width=8)
        type_lbl.pack(side=LEFT, padx=(15, 0))

        contains_opt = ttk.Radiobutton(
            master=type_row,
            text="包含",
            variable=self.type_var,
            value="contains"
        )
        contains_opt.pack(side=LEFT)

        startswith_opt = ttk.Radiobutton(
            master=type_row,
            text="开头",
            variable=self.type_var,
            value="startswith"
        )
        startswith_opt.pack(side=LEFT, padx=15)

        endswith_opt = ttk.Radiobutton(
            master=type_row,
            text="结尾",
            variable=self.type_var,
            value="endswith"
        )
        endswith_opt.pack(side=LEFT)
        endswith_opt.invoke()

        clear_btn = ttk.Button(
            master=type_row,
            text="重置",
            command=self.on_clear,
            bootstyle=DANGER,
            width=8
        )
        clear_btn.pack(side=RIGHT, padx=5)

    def create_results_view(self):
        """Add result treeview to labelframe"""
        self.resultview = ttk.Treeview(
            master=self,
            bootstyle=INFO,
            columns=[0, 1, 2, 3, 4],
            show=HEADINGS
        )
        self.resultview.pack(fill=BOTH, expand=YES, pady=10)

        # setup columns and use `scale_size` to adjust for resolution
        self.resultview.heading(0, text='名称', anchor=W)
        self.resultview.heading(1, text='修改日期', anchor=W)
        self.resultview.heading(2, text='类型', anchor=E)
        self.resultview.heading(3, text='大小', anchor=E)
        self.resultview.heading(4, text='路径', anchor=W)
        self.resultview.column(
            column=0,
            anchor=W,
            width=utility.scale_size(self, 125),
            stretch=False
        )
        self.resultview.column(
            column=1,
            anchor=W,
            width=utility.scale_size(self, 140),
            stretch=False
        )
        self.resultview.column(
            column=2,
            anchor=E,
            width=utility.scale_size(self, 50),
            stretch=False
        )
        self.resultview.column(
            column=3,
            anchor=E,
            width=utility.scale_size(self, 50),
            stretch=False
        )
        self.resultview.column(
            column=4,
            anchor=W,
            width=utility.scale_size(self, 300)
        )
        self.resultview.bind('<ButtonRelease-1>', self.get_tree_view_text)  # 绑定左键单击松开

    def on_browse(self):
        """Callback for directory browse"""
        path = filedialog.askdirectory(title="Browse directory")
        if path:
            self.path_var.set(path)

    def on_search(self):
        """Search for a term based on the search type"""
        search_term = self.term_var.get()
        search_path = self.path_var.get()
        search_type = self.type_var.get()

        if search_term == '':
            return

        if self.select_box_text == '文件名':
            # start search in another thread to prevent UI from locking
            Thread(target=FileSearchEngine.file_search, args=(search_term, search_path, search_type), daemon=True).start()
        else:
            Thread(target=self.find_text_in, args=(search_term, search_path, search_type), daemon=True).start()

        self.progressbar.start(10)

        iid = self.resultview.insert(parent='', index=END)
        self.resultview.item(iid, open=True)
        self.after(100, lambda: self.check_queue(iid))

    def check_queue(self, iid):
        """Check file queue and print results if not empty"""
        if all([
            FileSearchEngine.searching,
            not FileSearchEngine.queue.empty()
        ]):
            filename = FileSearchEngine.queue.get()
            self.insert_row(filename, iid)
            self.update_idletasks()
            self.after(100, lambda: self.check_queue(iid))
        elif all([
            not FileSearchEngine.searching,
            not FileSearchEngine.queue.empty()
        ]):
            while not FileSearchEngine.queue.empty():
                filename = FileSearchEngine.queue.get()
                self.insert_row(filename, iid)
            self.update_idletasks()
            self.progressbar.stop()
        elif all([
            FileSearchEngine.searching,
            FileSearchEngine.queue.empty()
        ]):
            self.after(100, lambda: self.check_queue(iid))
        else:
            self.progressbar.stop()

    def insert_row(self, file, iid):
        """Insert new row in tree search results"""
        try:
            _stats = file.stat()
            _name = file.stem
            _timestamp = datetime.datetime.fromtimestamp(_stats.st_mtime)
            _modified = _timestamp.strftime(r'%m/%d/%Y %I:%M:%S%p')
            _type = file.suffix.lower()
            _size = FileSearchEngine.convert_size(_stats.st_size)
            _path = file.as_posix()
            iid = self.resultview.insert(
                parent='',
                index=END,
                values=(_name, _modified, _type, _size, _path)
            )
            self.resultview.selection_set(iid)
            self.resultview.see(iid)
        except OSError:
            return

    @staticmethod
    def file_search(term, search_path, search_type):
        """Recursively search directory for matching files"""
        FileSearchEngine.set_searching(1)
        if search_type == 'contains':
            FileSearchEngine.find_contains(term, search_path)
        elif search_type == 'startswith':
            FileSearchEngine.find_startswith(term, search_path)
        elif search_type == 'endswith':
            FileSearchEngine.find_endswith(term, search_path)

    @staticmethod
    def find_contains(term, search_path):
        """Find all files that contain the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if term in file:
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.set_searching(False)

    @staticmethod
    def find_startswith(term, search_path):
        """Find all files that start with the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if file.startswith(term):
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.set_searching(False)

    @staticmethod
    def find_endswith(term, search_path):
        """Find all files that end with the search term"""
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    if file.endswith(term):
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.set_searching(False)

    @staticmethod
    def set_searching(state=False):
        """Set searching status"""
        FileSearchEngine.searching = state

    @staticmethod
    def convert_size(size):
        """Convert bytes to mb or kb depending on scale"""
        kb = size // 1000
        mb = round(kb / 1000, 1)
        if kb > 1000:
            return f'{mb:,.1f} MB'
        else:
            return f'{kb:,d} KB'

    @staticmethod
    def find_text_in(search_term, search_path, search_type):
        """文档内容查询"""
        FileSearchEngine.set_searching(1)
        print('文件内容搜索...，输出文件名: ', search_term, search_path, search_type)
        for path, _, files in pathlib.os.walk(search_path):
            if files:
                for file in files:
                    record = pathlib.Path(path) / file
                    file_text = read_file_text(record)
                    is_in = filter_term_in(search_term, file_text)
                    if is_in:
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.set_searching(False)

    def select_combobox(self, event):
        """获取下拉框所选"""
        for item in self.resultview.selection():
            item_text = self.resultview.item(item, 'values')
            print('下拉框', item_text)  # 点击的内容

    def on_clear(self):
        """重置"""
        x = self.resultview.get_children()
        for item in x:
            self.resultview.delete(item)

    def get_tree_view_text(self, event):
        """跳转到treeView点击的内容"""
        for item in self.resultview.selection():
            self.show_toast_notification('已跳转到目录')
            item_text = self.resultview.item(item, 'values')
            filedialog.askopenfilename(initialdir=item_text[4].replace('{}{}'.format(item_text[0], item_text[2]), ''))

    @staticmethod
    def show_toast_notification(msg):
        """系统提示"""
        toast = ToastNotification(
            title="消息提示",
            message=msg,
            duration=1000,
        )
        toast.show_toast()


if __name__ == '__main__':
    app = ttk.Window("文件搜索", "journal")  # journal
    FileSearchEngine(app)
    app.mainloop()
