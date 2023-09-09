import requests


class HeyJudeAPI:
    BASE_URL = "https://agent.heyjudeapp.com"

    def __init__(self, email, password, api_key):
        self.email = email
        self.password = password
        self.api_key = api_key
        self.token = self._authenticate()

    def _authenticate(self):
        endpoint = "/api/v1/auth/sign-in"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }
        payload = {
            "email": self.email,
            "password": self.password,
            "program": "heyjude",
            "platform": "web"
        }
        response = requests.post(self.BASE_URL + endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("token")

    def refresh_token(self):
        endpoint = "/api/v1/auth/refresh"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
        }
        response = requests.get(self.BASE_URL + endpoint, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_subscription_status(self):
        endpoint = "/api/v1/subscriptions/status"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
        }
        response = requests.get(self.BASE_URL + endpoint, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_open_tasks(self):
        endpoint = "/api/v1/tasks/open"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
        }
        response = requests.get(self.BASE_URL + endpoint, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_task_details(self, task_id):
        endpoint = f"/api/v1/tasks/{task_id}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "x-api-key": self.api_key,
        }
        response = requests.get(self.BASE_URL + endpoint, headers=headers)
        response.raise_for_status()
        return response.json()

    def send_task_message(self, task_id, message):
        endpoint = f"/api/v1/tasks/{task_id}/message"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        payload = {
            "type": "text",
            "text": message
        }
        response = requests.post(self.BASE_URL + endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def create_task(self, title, create_default_message=True):
        endpoint = "/api/v1/tasks/create"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        payload = {
            "title": title,
            "create_default_message": create_default_message
        }
        response = requests.post(self.BASE_URL + endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
