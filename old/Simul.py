#!/usr/bin/env python3
import mysql.connector
import time
from datetime import datetime
import uuid

DB_CONFIG = {
    'host': 'localhost',
    'user': 'domjudge',
    'password': 'domjudge',
    'database': 'domjudge',
    'port': 3306
}

# contest id:
CONTEST_ID = 2

SUBMISSIONS = [
     (13, 3, 3, 'correct'),
     # (119, 2, 1, 'correct'),
     # (205, 3, 1, 'correct'),
     # (5, 1, 2, 'correct'),
     # (75, 2, 2, 'correct'),
     # (246, 3, 2, 'correct'),
     # (12, 1, 3, 'correct'),
     # (98, 2, 3, 'correct')
]

SUBMISSIONS.sort(key=lambda x: x[0])

contest_start_cache = None


def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG, use_pure=True)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def get_contest_start_time():
    global contest_start_cache

    if contest_start_cache is not None:
        return contest_start_cache, time.time()

    conn = get_db_connection()
    if not conn:
        return None, None

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT starttime, UNIX_TIMESTAMP(NOW()) as now
            FROM contest 
            WHERE cid = %s
        """, (CONTEST_ID,))

        result = cursor.fetchone()

        if result:
            start_time = float(result[0])
            current_time = float(result[1])
            contest_start_cache = start_time
            return start_time, current_time
        else:
            print(f"Contest with id {CONTEST_ID} not found")
            return None, None

    except mysql.connector.Error as err:
        print(f"Error msg: {err}")
        return None, None
    finally:
        cursor.close()
        conn.close()


def wait_for_contest_start():

    while True:
        start_time, current_time = get_contest_start_time()

        if start_time is None:
            print(f"Can't fetch contest info")
            return None

        if current_time >= start_time:
            print(f"Contest started at {datetime.fromtimestamp(start_time).strftime('%H:%M:%S')}")
            return start_time

        wait_seconds = start_time - current_time
        print(f"Contest starts in {wait_seconds:.0f}s, ({datetime.fromtimestamp(start_time).strftime('%H:%M:%S')})")
        time.sleep(min(5, wait_seconds))


def insert_submission(team_id, prob_id, submit_time, result):
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Setting to rust compiler so that the judge host does not take it to judge
        cursor.execute("""
            INSERT INTO submission (cid, teamid, probid, langid, submittime, valid)
            VALUES (%s, %s, %s, 'rs', %s, 1)
        """, (CONTEST_ID, team_id, prob_id, submit_time))

        submit_id = cursor.lastrowid

        judging_uuid = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO judging (submitid, cid, result, verified, valid, seen, uuid, endtime)
            VALUES (%s, %s, %s, 1, 1, 1, %s, %s)
        """, (submit_id, CONTEST_ID, result, judging_uuid, submit_time))

        conn.commit()

        elapsed = submit_time - contest_start_cache
        elapsed_min = int(elapsed / 60)
        elapsed_sec = int(elapsed % 60)
        print(
            f"[+{elapsed_min:1d}:{elapsed_sec:02d}] Team{team_id:03d}, Problem {prob_id:2d} ({lang_id:4s}) = {result}")

        return True

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def run_simulation():
    conn = get_db_connection()

    print("get conn")
    if not conn:
        print("\nCould not connect to the database.")
        return
    conn.close()
    print("Connected")

    contest_start = wait_for_contest_start()
    if contest_start is None:
        return

    print(f"\nSimulation starting..")

    # one submission is (20, 9, 9, 'cpp', 'correct')
    for idx, (relative_time, team_id, prob_id, result) in enumerate(SUBMISSIONS, 1):
        submission_time = contest_start + (relative_time * 60)

        while True:
            current_time = time.time()
            if current_time >= submission_time:
                break

            wait_time = submission_time - current_time
            if wait_time > 10:
                elapsed = current_time - contest_start
                elapsed_min = int(elapsed / 60)
                elapsed_sec = int(elapsed % 60)
                print(f"⏰ [+{elapsed_min:1d}:{elapsed_sec:02d}] [{idx}/{len(SUBMISSIONS)}] Next in: {wait_time:.0f}s...")
                time.sleep(5)
            else:
                time.sleep(wait_time)

        insert_submission(team_id, prob_id, submission_time, result)


if __name__ == "__main__":
    print("start")
    try:
        run_simulation()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()