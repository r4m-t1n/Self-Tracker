import sys

from PyQt5.QtGui import QColor, QIcon, QLinearGradient, QPainter
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QPushButton, QWidget

from modules import ProgressWindow, TasksWindow, HabitsWindow, RecordWindow, database
from files import W_MAIN


class MainWindow(QMainWindow):
    def __init__(
        self,
    ):
        super().__init__()
        self.setWindowTitle("Self Tracker")
        self.setGeometry(600, 200, 720, 720)
        self.setWindowIcon(QIcon(W_MAIN))

        self.initUI()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())

        gradient.setColorAt(0.0, QColor("Violet"))
        gradient.setColorAt(0.5, QColor("SlateBlue"))
        gradient.setColorAt(1.0, QColor("MediumSeaGreen"))

        painter.fillRect(self.rect(), gradient)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.record_now = QPushButton("Record Now", self)
        self.record_now.setStyleSheet(
            "border-radius: 30px;"
            "background-color: #DB58FF;"
            "font-size: 50px;"
        )
        self.record_now.setFixedHeight(300)

        self.my_progress = QPushButton("My Progress", self)
        self.my_progress.setStyleSheet(
            "border-radius: 30px;"
            "background-color: #7179FF;"
            "font-size: 50px;"
        )
        self.my_progress.setFixedHeight(300)

        self.tasks = QPushButton("My Tasks", self)
        self.tasks.setStyleSheet(
            "border-radius: 30px;"
            "background-color: #FFCD36;"
            "font-size: 50px;"
        )
        self.tasks.setFixedHeight(300)

        self.habits = QPushButton("My Habits", self)
        self.habits.setStyleSheet(
            "border-radius: 30px;"
            "background-color: #70FF70;"
            "font-size: 50px;"
        )
        self.habits.setFixedHeight(300)

        grid_box = QGridLayout()

        grid_box.addWidget(self.record_now, 0, 0)
        grid_box.addWidget(self.my_progress, 0, 1)
        grid_box.addWidget(self.tasks, 1, 0)
        grid_box.addWidget(self.habits, 1, 1)
        central_widget.setLayout(grid_box)

        self.record_now.clicked.connect(self.record_now_)
        self.my_progress.clicked.connect(self.my_progress_)
        self.tasks.clicked.connect(self.tasks_)
        self.habits.clicked.connect(self.habits_)

    def record_now_(self):
        self.window_record = RecordWindow()
        self.window_record.show()
        self.window_record.setWindowTitle("Record Now")

    def my_progress_(self):
        self.window_progress = ProgressWindow()
        self.window_progress.show()
        self.window_progress.setWindowTitle("My Progress")

    def tasks_(self):
        self.window_tasks = TasksWindow()
        self.window_tasks.show()
        self.window_tasks.setWindowTitle("Tasks")

    def habits_(self):
        self.window_habits = HabitsWindow()
        self.window_habits.show()
        self.window_habits.setWindowTitle("Habits")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    database.setup_()
    main()
