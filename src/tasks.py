from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QLinearGradient, QPainter
from PyQt5.QtWidgets import (
    QButtonGroup,
    QCalendarWidget,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from db.db_handler import database
from message_boxes import MessageBox
from files import W_TASKS, ADD


class TasksWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(600, 200, 720, 720)
        self.setWindowIcon(QIcon(W_TASKS))

        self.main_layout = QVBoxLayout()
        self.buttons_layout = QGridLayout()
        self.tasks_layout = QGridLayout()

        self.scroll_ = QScrollArea()
        self.scroll_.setStyleSheet("background: transparent;")
        self.scroll_.viewport().setStyleSheet("background: transparent;")

        self.radio_button_group = QButtonGroup(self)

        self.load_tasks_()

        self.main_layout.addWidget(self.scroll_)
        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())

        gradient.setColorAt(0, QColor("#FF6B6B"))
        gradient.setColorAt(1, QColor("#FFD93D"))

        painter.fillRect(self.rect(), gradient)

    def initUI(self, pos: int = 0):
        self.change_task = QPushButton("Change Status", self)
        self.change_task.setStyleSheet(
            "font-size: 40px;"
            "border-radius: 10px;"
            "background-color: #A3E4B5;"
            "border: 2px solid #000000;"
        )
        self.change_task.clicked.connect(self.change_task_)

        self.add_task = QPushButton("Add a Task", self)
        self.add_task.setStyleSheet(
            "font-size: 40px;"
            "border-radius: 20px;"
            "background-color: #A3E4B5;"
            "border: 2px solid #000000;"
        )
        self.add_task.clicked.connect(self.add_task_)

        self.rmw_task = QPushButton("Delete a Task", self)
        self.rmw_task.setStyleSheet(
            "font-size: 40px;"
            "border-radius: 20px;"
            "background-color: #A3E4B5;"
            "border: 2px solid #000000;"
        )
        self.rmw_task.clicked.connect(self.rmw_task_)

        self.buttons_layout.addWidget(self.change_task, pos, 0, 1, 4)
        self.buttons_layout.addWidget(self.add_task, pos + 1, 0, 1, 2)
        self.buttons_layout.addWidget(self.rmw_task, pos + 1, 2, 1, 2)

    def load_tasks_(self):

        for k in reversed(range(self.tasks_layout.count())):
            self.tasks_layout.itemAt(k).widget().deleteLater()

        def create_separator():
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setFrameShadow(QFrame.Plain)
            line.setStyleSheet("border: 3px solid black;")
            return line

        tasks = database.get_tasks(True)

        row_count = len(tasks)

        if tasks:
            latest_row = 0
            for c, (task_id, task_name, deadline, status) in enumerate(tasks):
                task_button = QRadioButton(task_name, self)
                task_button.setStyleSheet("""
                    QRadioButton {
                        font-size: 20px;
                        color: black;
                    }
                    QRadioButton::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 10px;
                        border: 2px solid black;
                        background-color: transparent;
                    }
                    QRadioButton::indicator:checked {
                        background-color: black;
                        border: 2px solid black;
                    }
                """)
                self.radio_button_group.addButton(task_button, task_id)
                self.tasks_layout.addWidget(task_button, c + 2, 0, Qt.AlignCenter)

                deadline_label = QLabel(str(deadline))
                deadline_label.setStyleSheet("font-size: 20px;")
                self.tasks_layout.addWidget(deadline_label, c + 2, 2, Qt.AlignCenter)

                status_label = QLabel("Ongoing" if status is None else "Completed")
                status_label.setStyleSheet("font-size: 20px;")
                self.tasks_layout.addWidget(status_label, c + 2, 4, Qt.AlignCenter)

                latest_row = c

            self.tasks_layout.addWidget(create_separator(), 1, 1, row_count + 1, 1)
            self.tasks_layout.addWidget(create_separator(), 1, 3, row_count + 1, 1)

            self.tasks_widget = QWidget()
            self.tasks_widget.setLayout(self.tasks_layout)

            self.scroll_.setWidget(self.tasks_widget)
            self.scroll_.setWidgetResizable(True)

            if not self.buttons_layout:
                self.initUI(latest_row)

        else:
            if not self.buttons_layout:
                self.initUI()
            MessageBox().warning("There is no task here.")
            return

        self.h_line = QFrame()
        self.h_line.setFrameShape(QFrame.HLine)
        self.h_line.setFrameShadow(QFrame.Plain)
        self.h_line.setStyleSheet("border: 3px solid black;")
        self.tasks_layout.addWidget(self.h_line, 1, 0, 1, 5)

        self.task_label = QLabel("task")
        self.task_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.tasks_layout.addWidget(self.task_label, 0, 0, Qt.AlignCenter)

        self.deadline_label = QLabel("deadline")
        self.deadline_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.tasks_layout.addWidget(self.deadline_label, 0, 2, Qt.AlignCenter)

        self.to_label = QLabel("status")
        self.to_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.tasks_layout.addWidget(self.to_label, 0, 4, Qt.AlignCenter)

    def change_task_(self):
        if (id := self.radio_button_group.checkedId()) != -1:
            database.change_status(id)
            self.load_tasks_()

        else:
            MessageBox().error("You have not chosen a task.")

    def add_task_(self):
        self.window_add_task = AddTask()
        self.window_add_task.setWindowIcon(QIcon(ADD))
        self.window_add_task.show()
        self.window_add_task.task_added.connect(self.load_tasks_)
        self.window_add_task.setWindowTitle("Add a Task")

    def rmw_task_(self):
        if (id := self.radio_button_group.checkedId()) != -1:
            database.rmw_task(id)
            MessageBox().success(
                'Task "{}" is removed'.format(
                    self.radio_button_group.checkedButton().text()
                )
            )
            self.load_tasks_()

        else:
            MessageBox().error("You have not chosen a task.")


class AddTask(QWidget):

    task_added = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setGeometry(800, 300, 400, 200)

        self.date_time = None

        layout = QGridLayout()

        self.text = QLineEdit(self, placeholderText="write a task here", readOnly=False)
        layout.addWidget(self.text, 0, 0, 1, 3)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_button_)
        layout.addWidget(self.submit_button, 2, 0, 1, 3)

        self.deadline_label = QLabel("deadline")
        layout.addWidget(self.deadline_label, 1, 0, Qt.AlignCenter)

        self.select_date_button = QPushButton("Select date")
        self.select_date_button.clicked.connect(self.calendar_window_)
        layout.addWidget(self.select_date_button, 1, 1, Qt.AlignCenter)

        self.date_label = QLabel()
        layout.addWidget(self.date_label, 1, 2, Qt.AlignCenter)

        self.setLayout(layout)

    def submit_button_(self):
        if not self.date_time:
            MessageBox().error("You have not chosen a date.")
            return

        text = self.text.text()
        self.text.clear()
        self.date_label.clear()

        if len(text) >= 3:
            database.add_task(text, self.date_time)
            self.text.setPlaceholderText(
                "A new task has been submitted: {}".format(text)
            )
            self.task_added.emit()

        else:
            self.text.setPlaceholderText(
                "You have to enter a task with more than 3 letters!"
            )

    def calendar_window_(self):
        self.window_calendar = Calendar()
        self.window_calendar.show()
        self.window_calendar.setWindowTitle("Calendar")
        self.window_calendar.date_time.connect(self.get_date_)

    def get_date_(self, date: str):
        self.date_time = date
        self.date_label.setText(date)


class Calendar(QWidget):

    date_time = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.layout_calendar = QVBoxLayout()

        self.calendar = QCalendarWidget(self)
        self.calendar.setMinimumDate(QDate.currentDate().addDays(1))
        self.calendar.selectionChanged.connect(self.update_calendar_)
        self.layout_calendar.addWidget(self.calendar)

        self.setLayout(self.layout_calendar)

    def update_calendar_(self):
        self.selected_date = self.calendar.selectedDate()
        self.date_time.emit(self.selected_date.toString("yyyy-MM-dd"))
        self.destroy()
