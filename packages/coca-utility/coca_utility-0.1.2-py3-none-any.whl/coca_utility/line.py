import requests


class LineClient:
    def __init__(self, token: str):
        self.token = token

    def notify(self, msg: str) -> int:
        res = requests.post(
            "https://notify-api.line.me/api/notify",
            headers={"Authorization": f"Bearer {self.token}"},
            files={"message": (None, msg)},
        )
        return res.status_code
