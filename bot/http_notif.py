import requests
import json
import bot.auth as auth
from bot.config import config

def send_notif(message, channel=None):
    if channel is None:
        channel = config['notification_channel']
    baseURL = "https://discordapp.com/api/channels/%s/messages" % channel
    headers = {
        "Authorization":"Bot %s" % auth.token(),
        "User-Agent":"Platbot notifation (github.com/vivoe/turkish-delight-bot, v0.1)",
        "Content-Type":"application/json"
    }

    send_data = json.dumps({"content":message})

    r = requests.post(baseURL, headers=headers, data=send_data)
    return r
