import os

TOKEN = os.environ.get("TOKEN")
URL = os.environ.get("URL")


if TOKEN == None:
    TOKEN = "6766269713:AAG9hn1ticKkrcIrodGH_W1T9efac7h1oqQ"

if URL == None:
    URL = "https://5c91-88-241-48-214.ngrok-free.app"
