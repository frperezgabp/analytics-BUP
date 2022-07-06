from dotenv import load_dotenv
from pathlib import Path
import os
import json
import requests

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
AUTH = os.getenv("AUTH")

def get_header():
    url = "http://api.braveup.co/accounts/signin"
    payload = json.dumps({
    "email": 'back@braveup.cl',
    "password": 123456
    })
    headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiaWF0IjoxNjU0MjcwOTI1LCJleHAiOjE2NTY4NjI5MjV9.d4XyewUtD6Aib0LtzUGycdYrmBeijF-MyHYnlOSBc5U',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

    json.loads(response.text)['idToken']

    headers = {}
    headers['Authorization'] = 'Bearer '+json.loads(response.text)['idToken']
    headers['Content-Type'] = 'application/json'    
    return headers 
