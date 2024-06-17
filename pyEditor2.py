import tkinter as tk
from tkinter import ttk, filedialog, Text, Scrollbar, font

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("간단한 텍스트 에디터")
        self.root.geometry("800x600")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.open_files = {}  # 열린 파일들을 저장하는 딕셔너리

        self.create_menu()
        self.create_tab()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="새 파일", command=self.new_file)
        file_menu.add_command(label="열기", command=self.open_file)
        file_menu.add_command(label="저장", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        menu_bar.add_cascade(label="파일", menu=file_menu)

        self.root.config(menu=menu_bar)

    def create_tab(self, file_path=None):
        frame = ttk.Frame(self.tabs)

        text_widget = Text(frame, wrap=tk.WORD, font=("Arial", 10), foreground="black")
        text_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        scrollbar.config(command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

        line_numbers = Text(frame, width=3, wrap=tk.NONE, padx=3, takefocus=0, border=0, background='lightgrey', state=tk.DISABLED)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        line_numbers_font = font.Font(family="Arial", size=10)
        line_numbers.config(font=line_numbers_font, foreground="black")

        def update_line_numbers(event=None):
            lines = "\n".join(str(i) for i in range(1, int(text_widget.index(tk.END).split('.')[0])))
            line_numbers.config(state=tk.NORMAL)
            line_numbers.delete('1.0', tk.END)
            line_numbers.insert(tk.END, lines)
            line_numbers.config(state=tk.DISABLED)
            line_numbers.tag_add("center", "1.0", tk.END)
            line_numbers.tag_configure("center", justify='right', foreground='black')

        text_widget.bind('<KeyRelease>', update_line_numbers)
        text_widget.bind('<Configure>', update_line_numbers)

        frame.pack(fill=tk.BOTH, expand=True)

        if file_path:
            with open(file_path, "r") as file:
                text_widget.insert(tk.END, file.read())
            self.tabs.add(frame, text=file_path)
            self.open_files[frame] = file_path
        else:
            self.tabs.add(frame, text="새 파일")
            self.open_files[frame] = None

        self.tabs.select(frame)

    def new_file(self):
        self.create_tab()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
        if file_path:
            self.create_tab(file_path)

    def save_file(self):
        current_tab = self.tabs.select()
        current_frame = self.tabs.nametowidget(current_tab)
        file_path = self.open_files[current_frame]

        if file_path:
            with open(file_path, "w") as file:
                text_widget = current_frame.winfo_children()[0]
                file.write(text_widget.get("1.0", tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")])
        if file_path:
            current_tab = self.tabs.select()
            current_frame = self.tabs.nametowidget(current_tab)
            text_widget = current_frame.winfo_children()[0]
            with open(file_path, "w") as file:
                file.write(text_widget.get("1.0", tk.END))
            self.tabs.tab(current_tab, text=file_path)
            self.open_files[current_frame] = file_path

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()
