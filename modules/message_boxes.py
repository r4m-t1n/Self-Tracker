from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QWidget
from config import ERROR, WARNING, SUCCESS


class MessageBox(QWidget):
    def __init__(self):
        super().__init__()
        self.message_box = QMessageBox(self)

        self.error_icon = ERROR
        self.warning_icon = WARNING
        self.success_icon = SUCCESS

    def show_message_(self, title: str, text: str, icon_name: str):
        self.message_box.setWindowTitle(title)
        self.message_box.setText(text)
        self.message_box.setWindowIcon(QIcon(icon_name))
        self.message_box.exec()

    def success(self, text: str):
        self.show_message_("Successful!", text, self.success_icon)

    def error(self, text: str):
        self.show_message_("Error!", text, self.error_icon)

    def warning(self, text: str):
        self.show_message_("Warning!", text, self.warning_icon)
