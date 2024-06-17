import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QVBoxLayout, QWidget, QAction, QTabWidget, QPlainTextEdit, QSplitter
from PyQt5.QtGui import QFont, QTextCursor

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('간단한 텍스트 에디터')
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.open_files = {}  # 열린 파일들을 저장하는 딕셔너리

        self.create_menu()
        self.create_tab()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('파일')

        new_file_action = QAction('새 파일', self)
        new_file_action.triggered.connect(self.new_file)
        file_menu.addAction(new_file_action)

        open_file_action = QAction('열기', self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction('저장', self)
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        exit_action = QAction('종료', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def create_tab(self, file_path=None):
        tab = QWidget()
        layout = QVBoxLayout()

        splitter = QSplitter()
        line_numbers = QPlainTextEdit()
        line_numbers.setReadOnly(True)
        line_numbers.setMaximumWidth(40)
        line_numbers.setFont(QFont("Arial", 10))
        line_numbers.setStyleSheet("color: black; background-color: lightgrey;")
        splitter.addWidget(line_numbers)

        text_widget = QTextEdit()
        text_widget.setFont(QFont("Arial", 10))
        text_widget.setStyleSheet("color: black;")
        splitter.addWidget(text_widget)

        layout.addWidget(splitter)

        def update_line_numbers():
            lines = "\n".join(str(i) for i in range(1, text_widget.document().blockCount() + 1))
            line_numbers.setPlainText(lines)

            # Sync line numbers with the text area
            line_numbers.moveCursor(QTextCursor.End)
            text_widget.verticalScrollBar().setValue(text_widget.verticalScrollBar().value())

        text_widget.textChanged.connect(update_line_numbers)
        text_widget.verticalScrollBar().valueChanged.connect(lambda: line_numbers.verticalScrollBar().setValue(text_widget.verticalScrollBar().value()))
        text_widget.textChanged.emit()

        tab.setLayout(layout)
        self.tabs.addTab(tab, "새 파일" if file_path is None else file_path)

        if file_path:
            with open(file_path, "r") as file:
                text_widget.setPlainText(file.read())
            self.open_files[tab] = file_path
            update_line_numbers()
        else:
            self.open_files[tab] = None
            update_line_numbers()

    def new_file(self):
        self.create_tab()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '파일 열기', '', '텍스트 파일 (*.txt);;모든 파일 (*)')
        if file_path:
            self.create_tab(file_path)

    def save_file(self):
        current_tab_index = self.tabs.currentIndex()
        current_tab = self.tabs.widget(current_tab_index)
        file_path = self.open_files[current_tab]

        if file_path:
            with open(file_path, "w") as file:
                text_widget = current_tab.layout().itemAt(0).widget().widget(1)
                file.write(text_widget.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        current_tab_index = self.tabs.currentIndex()
        current_tab = self.tabs.widget(current_tab_index)
        file_path, _ = QFileDialog.getSaveFileName(self, '파일 저장', '', '텍스트 파일 (*.txt);;모든 파일 (*)')
        if file_path:
            text_widget = current_tab.layout().itemAt(0).widget().widget(1)
            with open(file_path, "w") as file:
                file.write(text_widget.toPlainText())
            self.tabs.setTabText(current_tab_index, file_path)
            self.open_files[current_tab] = file_path

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec_())
