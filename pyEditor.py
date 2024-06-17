import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QMessageBox, QTabWidget, QWidget
from PyQt5.QtGui import QFont, QFontMetrics, QPainter
from PyQt5.QtCore import Qt, QRect, QSize, QTimer

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

    def lineNumberAreaWidth(self):
        digits = 1
        current_widget = self.editor
        if current_widget and isinstance(current_widget, QTextEdit):
            max_value = max(1, current_widget.document().blockCount())
            while max_value >= 10:
                max_value /= 10
                digits += 1
            space = 3 + QFontMetrics(QFont("Arial", 12)).width('9') * digits
            return space
        return 0

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 메뉴 바
        menu_bar = self.menuBar()

        # 폰트 설정
        font = QFont("Arial", 14)

        # 파일 메뉴
        file_menu = menu_bar.addMenu('File')
        file_menu.setFont(font)

        new_action = QAction('New File', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        new_action.setFont(font)
        file_menu.addAction(new_action)

        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        open_action.setFont(font)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        save_action.setFont(font)
        file_menu.addAction(save_action)

        close_action = QAction('Close', self)
        close_action.setShortcut('Ctrl+W')
        close_action.triggered.connect(self.close_tab)
        close_action.setFont(font)
        file_menu.addAction(close_action)

        clear_action = QAction('Clear', self)
        clear_action.setShortcut('Ctrl+D')
        clear_action.triggered.connect(self.clear_text)
        clear_action.setFont(font)
        file_menu.addAction(clear_action)

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        exit_action.setFont(font)
        file_menu.addAction(exit_action)

        # 도움 메뉴
        help_menu = menu_bar.addMenu('Help')
        help_menu.setFont(font)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.about)
        about_action.setFont(font)
        help_menu.addAction(about_action)

        self.setWindowTitle('Simple Text Editor')
        self.setGeometry(100, 100, 600, 400)
        self.show()

    def new_file(self):
        text_edit = QTextEdit()
        font = QFont("Arial", 12)  # 폰트와 사이즈 설정
        text_edit.setFont(font)
        self.setLineNumberArea(text_edit)
        self.tab_widget.addTab(text_edit, 'Untitled')

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text Files (*.txt);;All Files (*.*)')
        if file_path:
            with open(file_path, 'r') as file:
                text_edit = QTextEdit()
                font = QFont("Arial", 12)  # 폰트와 사이즈 설정
                text_edit.setFont(font)
                text_edit.setText(file.read())
                self.setLineNumberArea(text_edit)
                self.tab_widget.addTab(text_edit, file_path.split('/')[-1])

    def save_file(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            current_index = self.tab_widget.currentIndex()
            tab_text = self.tab_widget.tabText(current_index)
            if tab_text == 'Untitled':
                file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Text Files (*.txt);;All Files (*.*)')
                if file_path:
                    with open(file_path, 'w') as file:
                        file.write(current_tab.toPlainText())
                    self.tab_widget.setTabText(current_index, file_path.split('/')[-1])
            else:
                with open(tab_text, 'w') as file:
                    file.write(current_tab.toPlainText())

    def close_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.removeTab(current_index)

    def clear_text(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            current_tab.clear()

    def about(self):
        QMessageBox.about(self, 'About', 'Simple Text Editor\nVersion 1.0')

    def setLineNumberArea(self, editor):
        self.lineNumberArea = LineNumberArea(editor)
        editor.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
        editor.cursorPositionChanged.connect(self.updateLineNumberArea)
        self.updateLineNumberArea()

    def lineNumberAreaWidth(self):
        digits = 1
        current_widget = self.tab_widget.currentWidget()
        if current_widget and isinstance(current_widget, QTextEdit):
            max_value = max(1, current_widget.document().blockCount())
            while max_value >= 10:
                max_value /= 10
                digits += 1
            space = 3 + QFontMetrics(QFont("Arial", 12)).width('9') * digits
            return space
        return 0

    def updateLineNumberArea(self):
        rect = QRect(0, 0, self.lineNumberArea.width(), self.lineNumberArea.height())
        self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if self.tab_widget.currentWidget():
            self.tab_widget.currentWidget().viewport().update()

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        font_metrics = QFontMetrics(QFont("Arial", 12))
        current_block = self.tab_widget.currentWidget().firstVisibleBlock()
        block_number = current_block.blockNumber()
        top = self.tab_widget.currentWidget().blockBoundingGeometry(current_block).translated(self.tab_widget.currentWidget().contentOffset()).top()
        bottom = top + self.tab_widget.currentWidget().blockBoundingRect(current_block).height()

        # Set pen color to black for line numbers
        painter.setPen(Qt.black)

        while current_block.isValid() and top <= event.rect().bottom():
            if current_block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, top, self.lineNumberArea.width(), font_metrics.height(), Qt.AlignRight, number)

            current_block = current_block.next()
            top = bottom
            bottom = top + self.tab_widget.currentWidget().blockBoundingRect(current_block).height()
            block_number += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    sys.exit(app.exec_())
