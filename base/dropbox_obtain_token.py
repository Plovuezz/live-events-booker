import requests
from requests.auth import HTTPBasicAuth

APP_KEY = "b574bh4wl14m7ck"
APP_SECRET = "l3akayj6upsdluv"

authorize_url = f"https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&token_access_type=offline&response_type=code"
print("1. Go to: " + authorize_url)
print('2. Click "Allow" (you might have to log in first).')
print("3. Copy the authorization code.")
auth_code = input("Enter the authorization code here: ").strip()

response = requests.post(
    "https://api.dropboxapi.com/oauth2/token",
    data={
        "code": auth_code,
        "grant_type": "authorization_code",
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    auth=HTTPBasicAuth(APP_KEY, APP_SECRET),
)

print(f"APP_KEY={APP_KEY}")
print(f"APP_SECRET={APP_SECRET}")
print(f"ACCESS_TOKEN={response.json()['access_token']}")
print(f"REFRESH_TOKEN={response.json()['refresh_token']}")
