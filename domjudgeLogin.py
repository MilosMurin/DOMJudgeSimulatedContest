import requests
from bs4 import BeautifulSoup

class LoginInfo:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def get_login_data(self):
        return {
            "_username": self.username,
            "_password": self.password
        }


class Domjudge:
    def __init__(self, login_info):
        self.session = requests.Session()
        self.login_info = login_info

    def set_contest(self, cid):
        self.session.cookies.set('domjudge_cid', str(cid))

    def login(self):
        login_url = "http://158.193.146.188/login"

        login_data = self.login_info.get_login_data()

        r = self.session.post(login_url, data=login_data)

        soup = BeautifulSoup(r.text, "html.parser")

        csrf = soup.find("input", {"name": "_csrf_token"})["value"]
        login_data["_csrf_token"] = csrf

        response = self.session.post(login_url, data=login_data)
        if response.status_code != 200:
            print(f'Login failed with {response.status_code}')
            print(response.text)
            raise Exception('Login failed')


        self.session.cookies.set('csrftoken', csrf)

    def call_update(self, submission_id):
        update_url = f"http://158.193.146.188/jury/submissions/{submission_id}/update-status"

        response = self.session.post(update_url, data={ 'valid': 'true' })

        if response.status_code != 200:
            if response.status_code != 404:
                print(f'Update failed with {response.status_code}')
                print(response.text)
            else:
                print(f'Just got a 404 haha :D')