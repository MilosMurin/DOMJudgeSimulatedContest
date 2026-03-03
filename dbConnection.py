import uuid

from mysql import connector

from data_loader import Submission


class DbConnection:

    def __init__(self, db_config):
        self.db_config = db_config
        pass

    def get_conn(self):
        try:
            conn = connector.connect(**self.db_config, use_pure=True)
            return conn
        except connector.Error as err:
            print(f"Error: {err}")
            return None

    def get_contest_start_time(self, contest_id):
        with self.get_conn() as conn:
            if not conn:
                return None, None

            with conn.cursor() as cursor:
                try:
                    cursor.execute("""SELECT starttime as now
                                   FROM contest WHERE cid = %s""", (contest_id,))

                    result = cursor.fetchone()

                    if result:
                        start_time = float(result[0])
                        return start_time
                    else:
                        print(f"Contest with id {contest_id} not found")
                        return None

                except connector.Error as err:
                    print(f"Error msg: {err}")
                    return None

    def insert_submission(self, contest_id, contest_start_time, submission: Submission):
        with self.get_conn() as conn:
            if not conn:
                return -1

            with conn.cursor() as cursor:

                try:
                    submit_time = contest_start_time + submission.submit_time_seconds
                    # Setting to rust compiler so that the judge host does not take it to judge
                    cursor.execute("""INSERT INTO submission (cid, teamid, probid, langid, submittime, valid)
                                   VALUES (%s, %s, %s, 'f95', %s, 1)""",
                                   (contest_id, submission.team_id, submission.problem_id, submit_time))

                    submit_id = cursor.lastrowid

                    judging_uuid = str(uuid.uuid4())
                    cursor.execute("""INSERT INTO judging (submitid, cid, result, verified, valid, seen, uuid, endtime)
                                   VALUES (%s, %s, %s, 1, 1, 1, %s, %s)""",
                                   (submit_id, contest_id, submission.result, judging_uuid, submit_time+1))

                    conn.commit()
                    return submit_id

                except connector.Error as e:
                    print(f"Error: {e}")
                    conn.rollback()
                    return -1