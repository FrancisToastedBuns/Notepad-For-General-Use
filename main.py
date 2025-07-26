import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QKeySequence, QAction, QFont, QPalette
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6.QtCore import pyqtBoundSignal


class TabBar(QTabBar):
    newTabRequested: 'pyqtBoundSignal' = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setExpanding(False)

        # Style the tab bar
        self.setStyleSheet("""
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: white;
                border-color: #0078d4;
                border-bottom: 2px solid #0078d4;
            }
            QTabBar::tab:hover:!selected {
                background: #e6f3ff;
            }
            QTabBar::close-button {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSI+PHBhdGggZD0iTTkgM0wzIDkiIHN0cm9rZT0iIzY2NiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjxwYXRoIGQ9Im0zIDMgNiA2IiBzdHJva2U9IiM2NjYiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz48L3N2Zz4=);
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
                background: #ff4444;
                border-radius: 2px;
            }
        """)

        self.plusButton = QPushButton("+")
        self.plusButton.setParent(self)
        self.plusButton.setFixedSize(32, 32)
        self.plusButton.setStyleSheet("""
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #106ebe;
            }
            QPushButton:pressed {
                background: #005a9e;
            }
        """)
        self.plusButton.clicked.connect(self.newTabRequested.emit)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updatePlusButtonPosition()

    def tabInserted(self, index):
        super().tabInserted(index)
        self.updatePlusButtonPosition()

    def tabRemoved(self, index):
        super().tabRemoved(index)
        self.updatePlusButtonPosition()

    def updatePlusButtonPosition(self):
        # Position the plus button right after the last tab
        if self.count() > 0:
            last_tab_rect = self.tabRect(self.count() - 1)
            x = last_tab_rect.right() + 8
            y = (self.height() - self.plusButton.height()) // 2
            self.plusButton.move(x, y)
        else:
            self.plusButton.move(8, (self.height() - self.plusButton.height()) // 2)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mesa's Notepad")
        self.setMinimumSize(800, 600)

        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 2px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #0078d4;
                color: white;
            }
            QPlainTextEdit {
                background-color: white;
                border: none;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                line-height: 1.4;
                padding: 10px;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background: white;
            }
        """)

        self.tabs = QTabWidget()
        tab_bar = TabBar(self.tabs)
        self.tabs.setTabBar(tab_bar)
        tab_bar.newTabRequested.connect(self.new_tab)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Set tab widget style
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background: white;
                border-top: none;
            }
        """)

        self.setCentralWidget(self.tabs)
        self.file_paths = {}

        self.create_menu_bar()
        self.new_tab()

    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Tab", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_action)

        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        close_tab_action = QAction("Close &Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(
            lambda: self.close_tab(self.tabs.currentIndex())
        )
        file_menu.addAction(close_tab_action)

    def closeEvent(self, e):
        for i in range(self.tabs.count()):
            text_edit = self.tabs.widget(i)
            if isinstance(text_edit, QPlainTextEdit) and text_edit.document().isModified():
                self.tabs.setCurrentIndex(i)
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Unsaved Changes")
                msg_box.setText(f"You have unsaved changes in tab {i + 1}. Save before closing?")
                msg_box.setIcon(QMessageBox.Icon.Question)
                msg_box.setStandardButtons(
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Save)

                # Style the message box
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                    }
                    QMessageBox QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #106ebe;
                    }
                """)

                answer = msg_box.exec()

                if answer == QMessageBox.StandardButton.Save:
                    self.save()
                    if text_edit.document().isModified():
                        e.ignore()
                        return
                elif answer == QMessageBox.StandardButton.Cancel:
                    e.ignore()
                    return

    def new_tab(self):
        text_edit = QPlainTextEdit()
        text_edit.setPlaceholderText("Start typing here...")

        # Set a nice font for the text editor
        font = QFont("Consolas", 12)
        if not font.exactMatch():
            font = QFont("Monaco", 12)
        if not font.exactMatch():
            font = QFont("monospace", 12)
        text_edit.setFont(font)

        index = self.tabs.addTab(text_edit, "Untitled")
        self.tabs.setCurrentIndex(index)
        text_edit.setFocus()
        return text_edit

    def close_tab(self, index):
        if self.tabs.count() <= 1:
            return

        current_tab = self.tabs.widget(index)
        if isinstance(current_tab, QPlainTextEdit) and current_tab.document().isModified():
            self.tabs.setCurrentIndex(index)
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Unsaved Changes")
            msg_box.setText("You have unsaved changes. Save before closing?")
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Save)

            # Style the message box
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #106ebe;
                }
            """)

            answer = msg_box.exec()

            if answer == QMessageBox.StandardButton.Save:
                self.save()
                if current_tab.document().isModified():
                    return
            elif answer == QMessageBox.StandardButton.Cancel:
                return

        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.new_tab()

    def save(self):
        current_index = self.tabs.currentIndex()
        current_tab = self.tabs.widget(current_index)
        if not isinstance(current_tab, QPlainTextEdit):
            return

        file_path = self.file_paths.get(current_index)
        if file_path is None:
            return self.save_as()
        else:
            try:
                with open(file_path, "w", encoding='utf-8') as f:
                    f.write(current_tab.toPlainText())
                current_tab.document().setModified(False)
                return True
            except Exception as e:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("Save Error")
                msg_box.setText(f"Failed to save file: {str(e)}")
                msg_box.exec()
                return False

    def save_as(self):
        current_index = self.tabs.currentIndex()
        current_tab = self.tabs.widget(current_index)
        if not isinstance(current_tab, QPlainTextEdit):
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save As", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*.*)"
        )
        if file_path:
            self.file_paths[current_index] = file_path
            filename = file_path.split("/")[-1].split("\\")[-1]
            self.tabs.setTabText(current_index, filename)
            return self.save()
        return False

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;Python Files (*.py);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    text = f.read()

                text_edit = self.new_tab()
                text_edit.setPlainText(text)

                current_index = self.tabs.currentIndex()
                self.file_paths[current_index] = file_path
                filename = file_path.split("/")[-1].split("\\")[-1]
                self.tabs.setTabText(current_index, filename)
                text_edit.document().setModified(False)
            except Exception as e:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("Open Error")
                msg_box.setText(f"Failed to open file: {str(e)}")
                msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application-wide font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())