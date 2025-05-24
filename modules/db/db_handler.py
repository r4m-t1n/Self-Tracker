import psycopg2
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(current_dir, "schema.sql")

HOST = os.environ.get("DB_HOST", "localhost")
DATABASE = os.environ.get("DB_NAME", "self-tracker")
USER = os.environ.get("DB_USER", "postgres")
PASSWORD = os.environ.get("DB_PASSWORD", "password")
PORT = os.environ.get("DB_PORT", 5432)

class Database:
    def __init__(self):

        self.connection_params = {
            "host": HOST,
            "dbname": DATABASE,
            "user": USER,
            "password": PASSWORD,
            "port": PORT,
        }

    def get_connection_(self):
        return psycopg2.connect(**self.connection_params)

    def setup_(self):
        setup_params = self.connection_params.copy()
        setup_params["dbname"] = "postgres"

        conn = psycopg2.connect(**setup_params)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DATABASE,))
            exists = cur.fetchone()

            if exists:
                return

            cur.execute('CREATE DATABASE %s', (DATABASE,))

        with self.get_connection_() as new_conn:
            with new_conn.cursor() as cur:
                with open(schema_path, "r") as file:
                    cur.execute(file.read())
                    new_conn.commit()

    def times_interference(self, time_: str):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    WITH condition_check AS (
                        SELECT EXISTS (
                            SELECT 1 
                            FROM habits
                            WHERE %s::TIME BETWEEN from_t AND to_t
                        ) AS valid_condition
                    )
                    SELECT valid_condition FROM condition_check;
                    """,
                    (time_,),
                )
                return cur.fetchone()[0]

    def get_habits(self, time=False):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT {} FROM habits ORDER BY from_t ASC".format(
                        "*" if time else "id, name"
                    )
                )
                return cur.fetchall()

    def add_habit(self, name: str, from_t: str, to_t: str):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:

                if self.times_interference(from_t) or self.times_interference(to_t):
                    return False

                cur.execute(
                    "INSERT INTO habits (id, name, from_t, to_t) VALUES ("
                    "COALESCE((SELECT MAX(id) FROM habits), 0) + 1, %s, %s, %s)",
                    (
                        name,
                        from_t,
                        to_t,
                    ),
                )
                conn.commit()

                return True

    def rmw_habit(self, id: int):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM habits WHERE id = %s", (id,))
                conn.commit()

    def get_tasks(self, deadline=False):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT {} FROM tasks ORDER BY deadline ASC, name".format(
                        "*" if deadline else "id, name"
                    )
                )
                return cur.fetchall()

    def add_task(self, name: str, deadline: str):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (id, name, deadline, is_done) VALUES ("
                    "COALESCE((SELECT MAX(id) FROM tasks), 0) + 1, %s, %s, NULL)",
                    (
                        name,
                        deadline,
                    ),
                )
                conn.commit()

    def rmw_task(self, id: int):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s", (id,))
                conn.commit()

    def change_status(self, id: int):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE tasks SET is_done = CURRENT_DATE WHERE id = %s", (id,)
                )
                conn.commit()

    def add_progress(self, id: int, is_habit: bool, time: int, date: str):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO progress (id, is_habit, time, date) VALUES ("
                    "%s, %s, %s, %s)",
                    (
                        id,
                        is_habit,
                        time,
                        date,
                    ),
                )
                conn.commit()

    def get_progress(self, is_habit: bool):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                results = []
                for days in [7, 42]:
                    cur.execute(
                        """
                        SELECT
                            SUM(time),
                            date FROM progress
                        WHERE CURRENT_DATE - date <= %s
                        AND is_habit = %s
                        GROUP BY date
                        ORDER BY date ASC""",
                        (
                            days,
                            is_habit,
                        ),
                    )
                    results.append(cur.fetchall())

                return results

    def get_progress_names(self):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        SUM(progress.time),
                        habits.name,
                        (habits.to_t - habits.from_t)
                    FROM progress
                    FULL JOIN habits ON habits.id = progress.id
                    WHERE CURRENT_DATE - progress.date <= 7
                    AND (habits.to_t - habits.from_t) IS NOT NULL
                    GROUP BY habits.name, habits.to_t, habits.from_t
                """
                )
                results = cur.fetchall()

                return results

    def get_streaks(self):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT date FROM progress WHERE is_habit = True")
                results = cur.fetchall()

                return results

    def total_time(self):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT SUM(time) FROM progress WHERE is_habit = True and date = CURRENT_DATE"
                )
                results = cur.fetchone()

                return results if results[0] is not None else 0

    def total_tasks(self):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM tasks WHERE is_done IS NOT NULL")
                results = cur.fetchone()

                return results if results[0] is not None else 0

    def this_week_tasks(self):
        with self.get_connection_() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM tasks WHERE is_done >= CURRENT_DATE - 7"
                )
                results = cur.fetchone()

                return results if results[0] is not None else 0


database = Database()
