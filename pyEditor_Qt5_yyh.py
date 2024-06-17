import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QMessageBox,
                             QTabWidget, QVBoxLayout, QWidget, QPlainTextEdit, QHBoxLayout, QTextEdit,
                             QFontDialog, QStatusBar, QDialog, QLabel, QLineEdit, QPushButton)
from PyQt5.QtGui import QFont, QPainter, QIcon, QTextCursor, QTextDocument, QColor, QTextFormat
from PyQt5.QtCore import Qt, QSize, QRect

'''
Program ID: pyEditor_Qt5_Ver001.py
Author    : Yun Young HUn
Date      : 2024-04-15
Version   : 20240415-001.Ver0.01 완성본 
            1.find기능 추가
            2.현재 편집 라인 배경색 추가
'''
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.scroll_value = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.editor.text_area.firstVisibleBlock()
        block_number = block.blockNumber()

        top = self.editor.text_area.blockBoundingGeometry(block).translated(self.editor.text_area.contentOffset()).top()
        bottom = top + self.editor.text_area.blockBoundingRect(block).height()

        # Adjust position and font
        font = self.editor.text_area.font()
        painter.setFont(font)
        painter.setPen(Qt.black)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1) + "  "  # Add a space after the number
                painter.drawText(0, top, self.width() - 5, font.pointSize() + 4, Qt.AlignRight, number)
           
            block = block.next()
            top = bottom
            bottom = top + self.editor.text_area.blockBoundingRect(block).height()
            block_number += 1

    def sizeHint(self):
        return QSize(50, self.editor.text_area.height())

    def scrollEvent(self, event):
        scrollbar = self.editor.text_area.verticalScrollBar()
        self.scroll_value = scrollbar.value()
        scrollbar.setValue(self.scroll_value)
        self.update()

class FindDialog(QDialog):
    def __init__(self, parent=None):
        super(FindDialog, self).__init__(parent)
        self.setWindowTitle('찾기')
        self.setWindowModality(Qt.WindowModal)  # 모달 다이얼로그로 설정

        layout = QVBoxLayout()

        self.find_label = QLabel('찾을 내용:')
        self.find_text_value = QLineEdit()
        self.find_button = QPushButton('찾기')
        self.find_button.clicked.connect(self.find_text)

        layout.addWidget(self.find_label)
        layout.addWidget(self.find_text_value)
        layout.addWidget(self.find_button)

        self.setLayout(layout)

    def find_text(self):
        text_to_find = self.find_text_value.text()
        editor = self.parent()

        if editor is not None:
            cursor = editor.text_area.textCursor()

            if text_to_find:
                editor.text_area.moveCursor(QTextCursor.Start)  # 시작 위치로 커서 이동
                editor.text_area.find(text_to_find, QTextDocument.FindFlags(0))  # 텍스트 찾기

                # 텍스트를 찾은 후 해당 행을 색으로 강조
                selections = []
                while editor.text_area.find(text_to_find, QTextDocument.FindFlags(0)):
                    selection = QTextEdit.ExtraSelection()
                    line_color = QColor(192, 192, 150, 50)  # RGBA 값 (192, 192, 192)와 투명도 150 설정
                    selection.format.setBackground(line_color)
                    selection.cursor = editor.text_area.textCursor()

                    # 행의 시작과 끝 위치 찾기
                    start_pos = selection.cursor.block().position()
                    end_pos = start_pos + selection.cursor.block().length() - 1

                    # 행 전체에 강조 설정
                    selection.cursor.setPosition(start_pos)
                    selection.cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
                    selections.append(selection)

                editor.text_area.setExtraSelections(selections)
                editor.text_area.ensureCursorVisible()

                if not selections:
                    QMessageBox.information(self, '찾기', '텍스트를 찾을 수 없습니다.')

class MyTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.setStyleSheet("background-color: white;")  # 흐린 회색 배경색 설정

    def highlight_current_line(self):
        extra_selections = []

        selection = QTextEdit.ExtraSelection()
        line_color = QColor(192, 192, 192, 80)  # RGBA 값 (192, 192, 192)와 투명도 150 설정

        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()

        extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text Editor by Python')
        self.setGeometry(100, 100, 900, 800)

        self.tabs = QTabWidget()        
        self.setCentralWidget(self.tabs)

        self.add_tab()

        new_action = QAction('새로 만들기', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.add_tab)

        open_action = QAction('열기', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)

        save_action = QAction('저장', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)

        save_as_action = QAction('다른 이름으로 저장', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_as)

        close_tab_action = QAction('탭 닫기', self)
        close_tab_action.setShortcut('Ctrl+W')
        close_tab_action.triggered.connect(self.close_tab)

        exit_action = QAction('종료', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)

        cut_action = QAction('잘라내기', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.cut)

        copy_action = QAction('복사하기', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.copy)

        paste_action = QAction('붙여넣기', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.paste)

        font_action = QAction('폰트', self)
        font_action.setShortcut('Ctrl+Shift+F')
        font_action.triggered.connect(self.choose_font)

        find_action = QAction('찾기', self)
        find_action.setShortcut('Ctrl+F')
        find_action.triggered.connect(self.show_find_dialog)        

        menubar = self.menuBar()
        file_menu = menubar.addMenu('파일')
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(close_tab_action)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu('편집')
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addAction(find_action)

        view_menu = menubar.addMenu('보기')
        view_menu.addAction(font_action)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def show_find_dialog(self):
        find_dialog = FindDialog(self)
        find_dialog.show()

    def add_tab(self):
        layout = QVBoxLayout()
        
        self.text_area = MyTextEdit()
        font = QFont("Arial", 10)
        self.text_area.setFont(font)

        self.text_area.cursorPositionChanged.connect(self.update_line_numbers)
        self.text_area.textChanged.connect(self.update_line_numbers)

        self.line_number_area = LineNumberArea(self)

        self.line_number_area.setFixedWidth(self.line_number_area_width())
        self.line_number_area.setFont(font)

        self.text_area.verticalScrollBar().valueChanged.connect(self.line_number_area.scrollEvent)
        self.text_area.horizontalScrollBar().valueChanged.connect(self.line_number_area.scrollEvent)

        h_box = QHBoxLayout()
        h_box.addWidget(self.line_number_area)
        h_box.addWidget(self.text_area)

        layout.addLayout(h_box)

        tab_widget = QWidget()
        tab_widget.setLayout(layout)
        self.tabs.addTab(tab_widget, '새 파일')
        self.tabs.setCurrentWidget(tab_widget)
        self.tabs.currentChanged.connect(self.update_current_tab)

    def update_current_tab(self, index):
        current_widget = self.tabs.widget(index)

        if current_widget:
            h_layout = current_widget.layout().itemAt(0)

            if h_layout:
                self.text_area = h_layout.itemAt(1).widget()
                self.line_number_area = h_layout.itemAt(0).widget()
                self.update_line_numbers()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '열기', '', '텍스트 파일 (*.txt);;모든 파일 (*)')

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                self.add_tab()

                self.text_area.setPlainText(content)
                self.tabs.setTabText(self.tabs.currentIndex(), file_path)
                self.update_line_numbers()

            except Exception as e:
                QMessageBox.critical(self, '오류', f'파일을 열 수 없습니다: {e}')

    def save_file(self):
        current_tab = self.tabs.currentIndex()
        tab_text = self.tabs.tabText(current_tab)

        if tab_text == '새 파일':
            self.save_as()
        else:
            file_path = tab_text
            content = self.text_area.toPlainText()

            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
            except Exception as e:
                QMessageBox.critical(self, '오류', f'파일을 저장할 수 없습니다: {e}')

    def save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '다른 이름으로 저장', '', '텍스트 파일 (*.txt);;모든 파일 (*)')

        if file_path:
            content = self.text_area.toPlainText()
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

                self.tabs.setTabText(self.tabs.currentIndex(), file_path)
            except Exception as e:
                QMessageBox.critical(self, '오류', f'파일을 저장할 수 없습니다: {e}')

    def close_tab(self):
        current_tab = self.tabs.currentIndex()
        self.tabs.removeTab(current_tab)

    def cut(self):
        self.text_area.cut()

    def copy(self):
        self.text_area.copy()

    def paste(self):
        self.text_area.paste()

    def choose_font(self):
        font, ok = QFontDialog.getFont(self.text_area.font(), self)

        if ok:
            self.text_area.setFont(font)
            self.update_line_numbers()

        self.tabs.currentChanged.connect(self.update_current_tab)

    def update_line_numbers(self):
        cursor = self.text_area.textCursor()
        block = cursor.block()
        line_count = block.blockNumber() + 1
        col_count = cursor.positionInBlock() + 1

        text = f"{self.tabs.tabText(self.tabs.currentIndex())} - 행: {line_count}, 열: {col_count}"
        self.statusBar.showMessage(text)

        self.line_number_area.setFixedWidth(self.line_number_area_width())
        self.line_number_area.update()

    def line_number_area_width(self):
        digits = len(str(self.text_area.blockCount()))

        if digits < 8:
            digits = 8

        space = 3 + self.text_area.fontMetrics().width('9') * digits
        return space

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec_())
