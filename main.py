import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtCore import Qt, pyqtSignal

class TabBar(QTabBar):
    newTabRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)

        self.plusButton = QPushButton("+")
        self.plusButton.setFixedSize(24, 24)
        self.plusButton.clicked.connect(self.newTabRequested.emit)

        if isinstance(parent, QTabWidget):
            parent.setCornerWidget(self.plusButton, Qt.Corner.TopRightCorner)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mesa's Notepad")

        self.tabs = QTabWidget()

        tab_bar = TabBar(self.tabs)
        self.tabs.setTabBar(tab_bar)

        tab_bar.newTabRequested.connect(self.new_tab)
        self.tabs.tabCloseRequested.connect(self.close_tab)

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
                msg_box.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Save)
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
        index = self.tabs.addTab(text_edit, "Untitled")
        self.tabs.setCurrentIndex(index)
        return text_edit

    def close_tab(self, index):
        if index <= 0:
            return

        current_tab = self.tabs.widget(index)
        if isinstance(current_tab, QPlainTextEdit) and current_tab.document().isModified():
            self.tabs.setCurrentIndex(index)
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Unsaved Changes")
            msg_box.setText("You have unsaved changes. Save before closing?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Save)
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
                with open(file_path, "w") as f:
                    f.write(current_tab.toPlainText())
                current_tab.document().setModified(False)
                return True
            except Exception as e:
                QMessageBox.warning(self, "Save Error", f"Failed to save file: {str(e)}")
                return False

    def save_as(self):
        current_index = self.tabs.currentIndex()
        current_tab = self.tabs.widget(current_index)
        if not isinstance(current_tab, QPlainTextEdit):
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save As", "", "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            self.file_paths[current_index] = file_path
            self.tabs.setTabText(current_index, file_path.split("/")[-1].split("\\")[-1])
            return self.save()
        return False

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    text = f.read()

                text_edit = self.new_tab()
                text_edit.setPlainText(text)

                current_index = self.tabs.currentIndex()
                self.file_paths[current_index] = file_path
                self.tabs.setTabText(current_index, file_path.split("/")[-1].split("\\")[-1])
                text_edit.document().setModified(False)
            except Exception as e:
                QMessageBox.warning(self, "Open Error", f"{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    #window.setWindowState(Qt::WindowMaximized)

    window.show()
    sys.exit(app.exec())
