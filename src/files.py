import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.dirname(CURRENT_DIR)

FOLDER = os.path.join(ROOT_DIR, "icons")

ERROR = os.path.join(FOLDER, "error.png")
WARNING = os.path.join(FOLDER, "warning.png")
SUCCESS = os.path.join(FOLDER, "success.png")

W_MAIN = os.path.join(FOLDER, "self_tracker.png")
W_HABITS = os.path.join(FOLDER, "window_habits.png")
W_TASKS = os.path.join(FOLDER, "window_tasks.png")
W_RECORD = os.path.join(FOLDER, "window_record.png")
W_PROGRESS = os.path.join(FOLDER, "window_progress.png")

ADD = os.path.join(FOLDER, "add.png")
RECORD = os.path.join(FOLDER, "record.png")
START = os.path.join(FOLDER, "start.png")
STOP = os.path.join(FOLDER, "stop.png")
PAUSE = os.path.join(FOLDER, "pause.png")
