import requests
import json

from config import config

url = f"https://sandbox.api.mailtrap.io/api/send/{config.API_URL}"
payload = {
    "from": {"email": "example@example.com", "name": "Mailtrap Test"},
    "to": [{"email": "gaafer.hajji1995@gmail.com", "name": "Jafar Loka"}],
    "Subject": "Jafar Loka Test",
    "text": "This Is The Test Of Sending Emails For Verification"
}

payload = json.dumps(payload)
headers = {
    "Authorization": f"Bearer {config.API_KEY}",
    "Content-Type": "application/json"
}
response = requests.request(method="POST", url=url, headers=headers, data=payload)
print(response.text)