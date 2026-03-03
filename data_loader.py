import csv


class Submission:
    def __init__(self, submit_time: int, problem_id: int, team_id: int, result: str):
        self.submit_time_seconds = submit_time * 60
        self.submit_time_minutes = submit_time
        self.problem_id = problem_id
        self.team_id = team_id
        self.result = result

    def __repr__(self):
        return f'Submission(Time:{self.submit_time_minutes}, Problem:{self.problem_id}, Team:{self.team_id}, Result:{self.result})'

    def team_problem_str(self):
        return f'Team{self.team_id:03d}, Problem {self.problem_id:2d} = {self.result}'

class Data:
    def __init__(self, file_name):
        self.file_name = file_name

        self.submissions = []

        with open(self.file_name, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                self.submissions.append(Submission(int(row[0]), int(row[1]), int(row[2]), row[3]))

        self.dataCount = len(self.submissions)
        self.index = 0

    def pos_str(self):
        return f'[{self.index}/{self.dataCount}]'

    def next(self):
        if self.index < self.dataCount:
            self.index += 1
            return self.submissions[self.index-1]
        else:
            return -1

    def hasNext(self):
        return self.index < self.dataCount - 1