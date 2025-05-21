import io
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import (
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .db.handling_data import database
from config import W_PROGRESS


class ProgressWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.showMaximized()
        self.setWindowIcon(QIcon(W_PROGRESS))

        self.vbox = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.tabBar().setExpanding(True)
        self.tabs.tabBar().setFont(QFont("Segoe UI", 11))

        self.tabs.setStyleSheet(
            """
            QTabBar::tab {
                background: #F7F7F7;
                color: #444;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 10px 24px;
                margin-right: 3px;
            }

            QTabBar::tab:selected {
                background: #FFFFFF;
                color: #000;
                border: 1px solid #aaa;
                border-bottom: 2px solid #FFFFFF;
            }

            QTabBar::tab:!selected {
                margin-top: 4px;
            }

            QTabWidget::pane {
                border: 1px solid #aaa;
                border-top: none;
                background: #FFFFFF;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                padding: 10px;
            }
        """
        )

        self.tabs.addTab(HabitsTab(), "habits")
        self.tabs.addTab(TasksTab(), "tasks")

        self.vbox.addWidget(self.tabs)

        self.setLayout(self.vbox)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("Violet"))
        gradient.setColorAt(0.5, QColor("SlateBlue"))
        gradient.setColorAt(1.0, QColor("MediumSeaGreen"))
        painter.fillRect(self.rect(), gradient)


class HabitsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.column = 0
        self.row = 0

        self.scroll_ = QScrollArea()
        self.scroll_.viewport().setStyleSheet("background: transparent;")
        self.scroll_.setStyleSheet("background: transparent;")

        self.graph_layout = QGridLayout()

        last_week, last_month = database.get_progress(True)

        data_of_goals = database.get_progress_names()

        df = pd.DataFrame(database.get_streaks(), columns=["date"])
        df["date"] = pd.to_datetime(df["date"])
        today = datetime.today().date()
        streak = 0

        for d in reversed(df["date"].dt.date):
            if d == today - timedelta(days=streak):
                streak += 1
            else:
                break

        self.streaks_label = QLabel("You have %s days on streak" % streak)
        self.streaks_label.setStyleSheet(
            "font-size: 25px;" "background-color: #FAFFFA;"
        )

        self.total_time = database.total_time()
        self.total_time_label = QLabel("You spent %s minutes today" % self.total_time)
        self.total_time_label.setStyleSheet(
            "font-size: 25px;" "background-color: #FAFFFA;"
        )

        card_inner_layout = QVBoxLayout()
        card_inner_layout.addWidget(self.streaks_label, alignment=Qt.AlignCenter)
        card_inner_layout.addWidget(self.total_time_label, alignment=Qt.AlignCenter)

        stats_card = QFrame()
        stats_card.setLayout(card_inner_layout)
        stats_card.setStyleSheet(
            "background-color: rgba(255, 255, 255, 200);"
            "border-radius: 15px;"
            "padding: 20px;"
        )

        self.graph_layout.addWidget(
            stats_card, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        space_label = QLabel()
        space_label.setFixedSize(1, 100)
        self.graph_layout.addWidget(
            space_label, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        self.last_week_graph = graph_goals_reached(data_of_goals)
        self.graph_layout.addWidget(
            self.last_week_graph, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        space_label = QLabel()
        space_label.setFixedSize(1, 100)
        self.graph_layout.addWidget(
            space_label, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        self.last_week_graph = graph_last_week(last_week)
        self.graph_layout.addWidget(
            self.last_week_graph, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        space_label = QLabel()
        space_label.setFixedSize(1, 100)
        self.graph_layout.addWidget(
            space_label, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        self.last_month_graph = graph_last_month(last_month)
        self.graph_layout.addWidget(
            self.last_month_graph, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.graph_layout)

        self.scroll_.setWidget(self.main_widget)
        self.scroll_.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_)
        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#C8E7FF"))
        gradient.setColorAt(1, QColor("#D8F9C4"))
        painter.fillRect(self.rect(), gradient)


class TasksTab(QWidget):
    def __init__(self):
        super().__init__()

        self.column = 0
        self.row = 0

        self.scroll_ = QScrollArea()
        self.scroll_.viewport().setStyleSheet("background: transparent;")
        self.scroll_.setStyleSheet("background: transparent;")
        self.graph_layout = QGridLayout()

        last_week, last_month = database.get_progress(False)

        self.this_week = database.this_week_tasks()
        self.this_week_label = QLabel(
            "You have done %s tasks this week" % self.this_week
        )
        self.this_week_label.setStyleSheet(
            "font-size: 25px;" "background-color: #FAFFFA;"
        )

        self.total_tasks = database.total_tasks()
        self.total_tasks_label = QLabel(
            "You have done %s tasks in total" % self.total_tasks
        )
        self.total_tasks_label.setStyleSheet(
            "font-size: 25px;" "background-color: #FAFFFA;"
        )

        card_inner_layout = QVBoxLayout()
        card_inner_layout.addWidget(self.this_week_label, alignment=Qt.AlignCenter)
        card_inner_layout.addWidget(self.total_tasks_label, alignment=Qt.AlignCenter)

        stats_card = QFrame()
        stats_card.setLayout(card_inner_layout)
        stats_card.setStyleSheet(
            "background-color: rgba(255, 255, 255, 200);"
            "border-radius: 15px;"
            "padding: 20px;"
        )

        self.graph_layout.addWidget(
            stats_card, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        space_label = QLabel()
        space_label.setFixedSize(1, 100)
        self.graph_layout.addWidget(
            space_label, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        self.last_week_graph = graph_last_week(last_week)
        self.graph_layout.addWidget(
            self.last_week_graph, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        space_label = QLabel()
        space_label.setFixedSize(1, 100)
        self.graph_layout.addWidget(
            space_label, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        self.last_month_graph = graph_last_month(last_month)
        self.graph_layout.addWidget(
            self.last_month_graph, self.row, self.column, 1, 2, Qt.AlignCenter
        )
        self.row += 1

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.graph_layout)

        self.scroll_.setWidget(self.main_widget)
        self.scroll_.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_)
        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())

        gradient.setColorAt(0, QColor("#B2FFCB"))
        gradient.setColorAt(1, QColor("#FFC78C"))

        painter.fillRect(self.rect(), gradient)


def graph_bar(
    data_frame: pd.DataFrame,
    interval: int,
    title: str,
    weeks: list = None,
):

    buf = io.BytesIO()

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    ax.set_ylabel("Time (in minutes)")

    data_frame["time"] = data_frame["time"].apply(lambda time: time // 60)

    x = data_frame["date"]
    y = data_frame["time"]

    if weeks:
        plt.bar(x, y, 5.5)
        plt.xticks(
            ticks=weeks, labels=[w.strftime("%Y-%m-%d") for w in weeks], rotation=45
        )
    else:
        ax.set_xlim(datetime.today() - timedelta(7), datetime.today())
        plt.bar(x, y)
        plt.xticks(rotation=45)

    plt.title(title, fontsize=15)
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()

    buf.seek(0)

    pix = QPixmap()
    pix.loadFromData(buf.getvalue())
    scaled_pix = pix.scaled(1000, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    rounded = rounded_pixmap(scaled_pix, 30)

    graph_label = QLabel()
    graph_label.setPixmap(rounded)

    return graph_label


def graph_last_week(data: tuple):
    data_frame = pd.DataFrame(data, columns=["time", "date"])

    return graph_bar(data_frame, 1, "Your progress in last 7 days")


def graph_last_month(data: tuple):
    data_frame = pd.DataFrame(data, columns=["time", "date"])
    data_frame["date"] = pd.to_datetime(data_frame["date"])

    end_date = datetime.today().date()

    raw_start = end_date - timedelta(weeks=6)
    start_date = raw_start - timedelta(days=raw_start.weekday())

    weeks = []
    current = start_date
    while current <= end_date:
        weeks.append(current)
        current += timedelta(days=7)

    data_frame = data_frame[data_frame["date"].dt.date >= start_date]
    data_frame["week_start"] = data_frame["date"].apply(
        lambda date: start_date
        + timedelta(days=((date.date() - start_date).days // 7) * 7)
    )

    time_values = []
    for week in weeks:
        window_start = week - timedelta(days=6)
        window_end = week
        window_sum = data_frame[
            (data_frame["date"].dt.date >= window_start)
            & (data_frame["date"].dt.date <= window_end)
        ]["time"].sum()
        time_values.append(window_sum)

    chart_df = pd.DataFrame({"date": weeks, "time": time_values})

    return graph_bar(
        chart_df, 7, "Your progress in last 6 weeks (starting from Mondays)", weeks
    )


def graph_goals_reached(data: tuple):
    data_frame = pd.DataFrame(data, columns=["time", "name", "goal"])
    if not data_frame.empty:
        data_frame["time"] = data_frame["time"].apply(lambda time: time // 60)
        data_frame["goal"] = (data_frame["goal"] // pd.Timedelta(minutes=1)).astype(
            "int64"
        )

    buf = io.BytesIO()

    y_pos = list(range(len(data)))

    plt.figure(figsize=(8, 4))

    for i, row in data_frame.iterrows():
        done = row["time"]
        target = row["goal"]

        if done <= target:
            plt.barh(i, done, color="red", height=0.5)
        else:
            plt.barh(i, target, color="red", height=0.5)
            plt.barh(i, done - target, left=target, color="green", height=0.5)

    plt.yticks(y_pos, data_frame["name"])
    plt.xlabel("Minutes")
    plt.title("Goals you have reached", fontsize=15)
    plt.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()

    buf.seek(0)

    pix = QPixmap()
    pix.loadFromData(buf.getvalue())
    scaled_pix = pix.scaled(1000, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    rounded = rounded_pixmap(scaled_pix, 30)

    graph_label = QLabel()
    graph_label.setPixmap(rounded)

    return graph_label


def rounded_pixmap(pixmap, radius):
    size = pixmap.size()
    rounded = QPixmap(size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size.width(), size.height()), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return rounded
