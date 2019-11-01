import logging
import os
import socket
from datetime import datetime
from enum import Enum

import requests

logger = logging.getLogger(__name__)
Status = Enum("Status", "Success Warning Error")
webhook = os.environ["SLACK_WEBHOOK"]
slack_channel = os.environ.get("SLACK_CHANNEL", "general")

payload = {
    "channel": slack_channel,
    "username": "Talebot",
    "icon_emoji": ":taleb:",
    "attachments": [{
        'author_name': socket.getfqdn(),
        "footer": "Talebot"
    }]
}


def slack_notification(text, status=Status.Error):
    """Post Slack notification"""
    title = "Backup status report"
    color = "#ff9906"
    msg = text

    payload["attachments"][0]["fallback"] = msg
    payload["attachments"][0]["text"] = msg
    payload["attachments"][0]["color"] = color
    payload["attachments"][0]["title"] = title
    payload["attachments"][0]["ts"] = datetime.today().timestamp()

    response = requests.post(webhook, json=payload)

    if response.status_code != 200:
        msg = "Error connecting to Slack {}. Response is:\n{}".format(
            response.status_code, response.text)
        logger.error(msg)
