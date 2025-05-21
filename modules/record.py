from PyQt5.QtCore import QDate, QSize, Qt, QTime, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QLinearGradient, QPainter
from PyQt5.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from .db.db_handler import database
from .message_boxes import MessageBox
from config import W_RECORD, RECORD, START, PAUSE, STOP


class RecordWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(600, 200, 720, 720)
        self.setWindowTitle("Record Window")
        self.setWindowIcon(QIcon(W_RECORD))

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        content_layout = QHBoxLayout()

        self.select_button = QPushButton("Select")
        self.select_button.setStyleSheet("font-size: 20px;")
        self.select_button.clicked.connect(self.select_button_)
        top_layout.addStretch()
        top_layout.addWidget(self.select_button)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        self.radio_button_group = QButtonGroup(self)
        self.radio_button_group.setExclusive(True)

        self.radio_buttons = dict()

        habits_box = QGroupBox("Habits")
        habits_box.setStyleSheet(
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; color: white; }"
        )
        habits_layout = QVBoxLayout()

        habits = database.get_habits()
        if habits:
            for habit_id, habit_name in habits:
                button = QRadioButton(habit_name)
                button.setStyleSheet("font-size: 16px; color: white;")
                self.radio_buttons[button] = {"id": habit_id, "is_habit": True}
                self.radio_button_group.addButton(button)
                habits_layout.addWidget(button)
        else:
            warning_label = QLabel("There is no habit here")
            warning_label.setStyleSheet("font-size: 20px;")
            habits_layout.addWidget(warning_label, alignment=Qt.AlignCenter)

        habits_box.setLayout(habits_layout)

        tasks_box = QGroupBox("Tasks")
        tasks_box.setStyleSheet(
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; color: white; }"
        )
        tasks_layout = QVBoxLayout()

        tasks = database.get_tasks()
        if tasks:
            for task_id, task_name in tasks:
                button = QRadioButton(task_name)
                button.setStyleSheet("font-size: 16px; color: white;")
                self.radio_buttons[button] = {"id": task_id, "is_habit": False}
                self.radio_button_group.addButton(button)
                tasks_layout.addWidget(button)
        else:
            warning_label = QLabel("There is no task here")
            warning_label.setStyleSheet("font-size: 20px;")
            tasks_layout.addWidget(warning_label, alignment=Qt.AlignCenter)

        tasks_box.setLayout(tasks_layout)

        content_layout.addWidget(habits_box)
        content_layout.addWidget(tasks_box)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())

        gradient.setColorAt(0.0, QColor("#1F1C2C"))
        gradient.setColorAt(0.5, QColor("#928DAB"))

        gradient.setColorAt(1.0, QColor("#2C3E50"))

        painter.fillRect(self.rect(), gradient)

    def select_button_(self):
        selected_button = self.radio_button_group.checkedButton()
        if selected_button is None:
            MessageBox().error("You have not chosen anything.")
            return

        self.information = self.radio_buttons[selected_button]
        self.recording_progress = RecordingProgress()
        self.recording_progress.setWindowTitle("Recording Progress")
        self.recording_progress.sending_signal.connect(self.add_progress_)
        self.recording_progress.sending_time.connect(self.get_time_)
        self.recording_progress.show()

    def add_progress_(self):
        database.add_progress(
            *self.information.values(),
            self.time,
            QDate().currentDate().toString("yyyy-MM-dd")
        )

    def get_time_(self, seconds):
        self.time = seconds


class RecordingProgress(QWidget):

    sending_signal = pyqtSignal()
    sending_time = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setGeometry(600, 200, 720, 720)
        self.setStyleSheet("background-color: #E1E2FF;")
        self.setWindowIcon(QIcon(RECORD))

        self.grid_box = QGridLayout()

        self.current_time = QTime(00, 00, 00)
        self.timer_label = QLabel(self.current_time.toString("hh : mm : ss"))
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_)
        self.timer_label.setStyleSheet("font-size: 80px;")
        self.grid_box.addWidget(self.timer_label, 0, 1, Qt.AlignCenter)

        self.stop_button = QPushButton(self)
        self.stop_button.setIcon(QIcon(STOP))
        self.stop_button.setIconSize(QSize(75, 75))
        self.stop_button.setFixedSize(300, 85)
        self.stop_button.clicked.connect(self.stop_button_)
        self.grid_box.addWidget(self.stop_button, 1, 0)

        self.pause_button = QPushButton(self)
        self.pause_button.setIcon(QIcon(PAUSE))
        self.pause_button.setIconSize(QSize(75, 75))
        self.pause_button.clicked.connect(self.pause_button_)
        self.grid_box.addWidget(self.pause_button, 1, 1)

        self.start_button = QPushButton(self)
        self.start_button.setIcon(QIcon(START))
        self.start_button.setIconSize(QSize(75, 75))
        self.start_button.setFixedSize(300, 85)
        self.start_button.clicked.connect(self.start_button_)
        self.grid_box.addWidget(self.start_button, 1, 2)

        self.setLayout(self.grid_box)

    def stop_button_(self):

        seconds = QTime(0, 0, 0).secsTo(self.current_time)

        self.timer.stop()
        self.current_time = QTime(00, 00, 00)
        self.timer_label.setText(self.current_time.toString("hh : mm : ss"))

        if not self.start_button.isEnabled():
            self.start_button.setEnabled(True)

        if not self.pause_button.isEnabled():
            self.pause_button.setEnabled(True)

        if seconds < 60:
            MessageBox().warning(
                "Your progress will not be saved, because it is less than 60 seconds."
            )
            return

        self.sending_time.emit(seconds)
        self.sending_signal.emit()

        MessageBox().success("Your progress successfully saved.")

    def pause_button_(self):
        self.timer.stop()
        if not self.start_button.isEnabled():
            self.start_button.setEnabled(True)

        self.pause_button.setEnabled(False)

    def start_button_(self):
        if not self.pause_button.isEnabled():
            self.pause_button.setEnabled(True)

        self.start_button.setEnabled(False)
        self.timer.start(1000)

    def time_(self):
        self.current_time = self.current_time.addSecs(1)
        self.timer_label.setText(self.current_time.toString("hh : mm : ss"))
