from PyQt5.QtCore import Qt, QTime, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QLinearGradient, QPainter
from PyQt5.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from .db.db_handler import database
from .message_boxes import MessageBox
from config import W_HABITS, ADD


class HabitsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(600, 200, 720, 720)
        self.setWindowIcon(QIcon(W_HABITS))

        self.main_layout = QVBoxLayout()
        self.buttons_layout = QGridLayout()
        self.habits_layout = QGridLayout()

        self.scroll_ = QScrollArea()
        self.scroll_.setStyleSheet("background: transparent;")
        self.scroll_.viewport().setStyleSheet("background: transparent;")

        self.radio_button_group = QButtonGroup(self)

        self.load_habits_()

        self.main_layout.addWidget(self.scroll_)
        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())

        gradient.setColorAt(0, QColor("#E3F2FD"))
        gradient.setColorAt(1, QColor("#D0F0E0"))

        painter.fillRect(self.rect(), gradient)

    def initUI(self, pos: int = 0):

        self.add_habit = QPushButton("Add a Habit", self)
        self.add_habit.setStyleSheet(
            "font-size: 40px;"
            "border-radius: 20px;"
            "background-color: rgb(255, 244, 200);"
            "border: 2px solid #000000;"
        )
        self.add_habit.clicked.connect(self.add_habit_)

        self.rmw_habit = QPushButton("Delete a Habit", self)
        self.rmw_habit.setStyleSheet(
            "font-size: 40px;"
            "border-radius: 20px;"
            "background-color: rgb(255, 244, 200);"
            "border: 2px solid #000000;"
        )
        self.rmw_habit.clicked.connect(self.rmw_habit_)

        self.buttons_layout.addWidget(self.add_habit, pos + 1, 0, 1, 2)
        self.buttons_layout.addWidget(self.rmw_habit, pos + 1, 2, 1, 2)

    def load_habits_(self):

        for k in reversed(range(self.habits_layout.count())):
            self.habits_layout.itemAt(k).widget().deleteLater()

        def create_separator():
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setFrameShadow(QFrame.Plain)
            line.setStyleSheet("border: 3px solid black;")
            return line

        habits = database.get_habits(True)

        row_count = len(habits)

        if habits:
            latest_row = 0
            for c, (habit_id, habit_name, from_t, to_t) in enumerate(habits):
                habit_button = QRadioButton(habit_name, self)
                habit_button.setStyleSheet("font-size: 20px;")
                self.radio_button_group.addButton(habit_button, habit_id)
                self.habits_layout.addWidget(habit_button, c + 2, 0, Qt.AlignCenter)

                from_t_ = QLabel(str(from_t))
                from_t_.setStyleSheet("font-size: 20px;")
                self.habits_layout.addWidget(from_t_, c + 2, 2, Qt.AlignCenter)

                to_t_ = QLabel(str(to_t))
                to_t_.setStyleSheet("font-size: 20px;")
                self.habits_layout.addWidget(to_t_, c + 2, 4, Qt.AlignCenter)

                latest_row = c

            self.habits_layout.addWidget(create_separator(), 1, 1, row_count + 1, 1)
            self.habits_layout.addWidget(create_separator(), 1, 3, row_count + 1, 1)

            self.habits_widget = QWidget()
            self.habits_widget.setLayout(self.habits_layout)

            self.scroll_.setWidget(self.habits_widget)
            self.scroll_.setWidgetResizable(True)

            if not self.buttons_layout:
                self.initUI(latest_row)

        else:
            if not self.buttons_layout:
                self.initUI()

            MessageBox().warning("There is no habit here.")
            return

        self.h_line = QFrame()
        self.h_line.setFrameShape(QFrame.HLine)
        self.h_line.setFrameShadow(QFrame.Plain)
        self.h_line.setStyleSheet("border: 3px solid black;")
        self.habits_layout.addWidget(self.h_line, 1, 0, 1, 5)

        self.habit_label = QLabel("habit")
        self.habit_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.habits_layout.addWidget(self.habit_label, 0, 0, Qt.AlignCenter)

        self.from_label = QLabel("from")
        self.from_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.habits_layout.addWidget(self.from_label, 0, 2, Qt.AlignCenter)

        self.to_label = QLabel("to")
        self.to_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.habits_layout.addWidget(self.to_label, 0, 4, Qt.AlignCenter)

    def add_habit_(self):
        self.window_add_habit = AddHabit()
        self.window_add_habit.setWindowIcon(QIcon(ADD))
        self.window_add_habit.show()
        self.window_add_habit.habit_added.connect(self.load_habits_)
        self.window_add_habit.setWindowTitle("Add a Habit")

    def rmw_habit_(self):
        if (id := self.radio_button_group.checkedId()) != -1:
            database.rmw_habit(id)
            MessageBox().success(
                'Habit "{}" is removed'.format(
                    self.radio_button_group.checkedButton().text()
                )
            )
            self.load_habits_()

        else:
            MessageBox().error("You have not chosen a habit.")


class AddHabit(QWidget):

    habit_added = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setGeometry(800, 300, 400, 200)

        layout = QGridLayout()

        self.text = QLineEdit(
            self, placeholderText="write a habit here", readOnly=False
        )
        layout.addWidget(self.text, 0, 0, 1, 4)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_button_)
        layout.addWidget(self.submit_button, 2, 0, 1, 4)

        self.from_label = QLabel("from")
        layout.addWidget(self.from_label, 1, 0, Qt.AlignCenter)

        self.time_picker_from = QTimeEdit(self)
        self.time_picker_from.setTime(QTime(12, 0))
        self.time_picker_from.setDisplayFormat("HH:mm")
        self.time_picker_from.timeChanged.connect(self.update_time_)
        layout.addWidget(self.time_picker_from, 1, 1, Qt.AlignCenter)

        self.to_label = QLabel("to")
        layout.addWidget(self.to_label, 1, 2, Qt.AlignCenter)

        self.time_picker_to = QTimeEdit(self)
        self.time_picker_to.setTime(QTime(12, 5))
        self.time_picker_to.setDisplayFormat("HH:mm")
        layout.addWidget(self.time_picker_to, 1, 3, Qt.AlignCenter)

        self.update_time_()

        self.setLayout(layout)

    def update_time_(self):
        max_time = self.time_picker_from.time().addSecs(21600)
        self.time_picker_to.setMaximumTime(max_time)

        min_time = self.time_picker_from.time().addSecs(300)
        self.time_picker_to.setMinimumTime(min_time)

    def submit_button_(self):
        text = self.text.text()
        self.text.clear()

        if len(text) >= 3:
            if not database.add_habit(
                text, self.time_picker_from.text(), self.time_picker_to.text()
            ):
                MessageBox().error(
                    "You cannot choose a time between your previous chosen times."
                )
                return

            self.text.setPlaceholderText(
                "A new habit has been submitted: {}".format(text)
            )
            self.habit_added.emit()

        else:
            self.text.setPlaceholderText(
                "You have to enter a habit with more than 3 letters!"
            )
