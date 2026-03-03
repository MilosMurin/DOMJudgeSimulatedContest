import time
from datetime import datetime

from data_loader import Data, Submission
from dbConnection import DbConnection
from domjudgeLogin import Domjudge


class SimulatedContest:

    def __init__(self, db_config, contest_id, login_info, data_file):
        self.data = Data(data_file)
        self.contest_id = contest_id
        self.db = DbConnection(db_config)

        self.domjudge = Domjudge(login_info)

        self.domjudge.login()

        self.start_time = self.db.get_contest_start_time(self.contest_id)

    def run_simulation(self):
        if not self.wait_for_contest_start():
            return

        while self.data.hasNext():
            submission = self.data.next()

            submission_time = self.start_time + submission.submit_time_seconds

            while True:
                current_time = time.time()
                if current_time >= submission_time:
                    break

                wait_time = submission_time - current_time
                if wait_time > 10:
                    elapsed = current_time - self.start_time
                    elapsed_min = int(elapsed / 60)
                    elapsed_sec = int(elapsed % 60)
                    print(f"⏰ [+{elapsed_min:1d}:{elapsed_sec:02d}] {self.data.pos_str()} Next in: {wait_time:.0f}s...")
                    time.sleep(5)
                else:
                    time.sleep(wait_time)

            self.insert_submission(submission)

    def wait_for_contest_start(self):

        while True:
            if self.start_time is None:
                print(f"Can't fetch contest info")
                return False

            if time.time() >= self.start_time:
                print(f"Contest started at {datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')}")
                return True

            wait_seconds = self.start_time - time.time()
            print(f"Contest starts in {wait_seconds:.0f}s, ({datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')})")
            time.sleep(min(5, wait_seconds))

    def insert_submission(self, submission: Submission):

        submit_id = self.db.insert_submission(self.contest_id, self.start_time, submission)

        if submit_id < 0:
            print(f'Failed to insert submission {submission}')
        else:
            print('Updating score cache')
            # self.domjudge.login()

            self.domjudge.call_update(submit_id)

            elapsed = submission.submit_time_seconds - self.start_time
            elapsed_min = int(elapsed / 60)
            elapsed_sec = int(elapsed % 60)
            print(f"[+{elapsed_min:1d}:{elapsed_sec:02d}] {submission.team_problem_str()}")
