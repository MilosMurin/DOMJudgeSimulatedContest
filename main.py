from domjudgeLogin import LoginInfo
from simulation import SimulatedContest


DATA_FILE = 'submissions.csv'
CONTEST_ID = 123


DB_CONFIG = {}

with open('dblogin.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        spl = line.strip().split(':')
        DB_CONFIG[spl[0]] = spl[1]


LOGIN_INFO = None

with open('domjudgelogin.txt', 'r') as f:
    lines = f.readlines()
    LOGIN_INFO = LoginInfo(lines[0].strip(), lines[1].strip(), lines[2].strip())


if LOGIN_INFO is None:
    raise ValueError('Failed to parse login info')

if __name__ == "__main__":
    try:
        contest = SimulatedContest(DB_CONFIG, CONTEST_ID, LOGIN_INFO, DATA_FILE)
        print("start")
        contest.run_simulation()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()