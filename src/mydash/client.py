import requests
from .widgets import BaseWidget, TextWidget

class Client():
    def __init__(self, *, id: str, password: str, endpoint: str = "https://dashboard-api.llms.kr"):
        self.session = requests.session()
        self.endpoint = endpoint
        result = requests.post(f"{endpoint}/api/collections/users/auth-with-password", json={
            'identity': id,
            'password': password,
        })
        response = result.json()
        if 'token' not in response:
            raise Exception('Login failed. Check your identiy and password.')
        self.token = response['token']
        self.uid = response['record']['id']
        self.session.headers['Authorization'] = self.token
        self.session.headers["Content-Type"] = "application/json"
        print("Login success!")
    
    def _get_widgets_list(self, n: int = 50):
        result = self.session.get(f"{self.endpoint}/api/collections/widgets/records", params={
            'perPage': n,
            'sort': 'order',
            'filter': f'author = "{self.uid}"',
        }, headers={

        })
        return result['items']

    def create_text_widget(self, name: str, title: str) -> TextWidget:
        widget = TextWidget(name=name, title=title, author=self.uid)
        return widget

    def push_widget(self, widget: BaseWidget):
        exists = self.session.get(f"{self.endpoint}/api/collections/widgets/records", params={
            "filter": f'name = "{widget.name}"',
        })
        if not exists.ok:
            raise Exception(exists.text)
        data = exists.json()
        if data['totalItems'] >= 1:
            id = data['items'][0]['id']
            result = self.session.patch(f"{self.endpoint}/api/collections/widgets/records/{id}", data=widget.toJSON())
            if not result.ok:
                raise Exception(result.text)
        else:
            result = self.session.post(f"{self.endpoint}/api/collections/widgets/records", data=widget.toJSON())
            if not result.ok:
                raise Exception(result.text)()
    
    def remove_widget(self, name: str):
        exists = self.session.get(f"{self.endpoint}/api/collections/widgets/records", params={
            "filter": f'name = "{name}"',
        })
        if not exists.ok:
            raise Exception(exists.text)
        data = exists.json()
        if data['totalItems'] >= 1:
            id = data['items'][0]['id']
            result = self.session.delete(f"{self.endpoint}/api/collections/widgets/records/{id}")
            if not result.ok:
                raise Exception(result.text)

