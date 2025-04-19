import logging

import httpx

from social_network.config import config

import smtplib as smtp

logger = logging.getLogger(__name__)

async def send_simple_email(to: str, subject: str, body: str, from_: str):
    sender = f"Private Person <{from_}>"
    receiver = f"A Test User <{to}>"

    message = f"""\
        Subject: {subject}
        To: {receiver}
        From: {sender}

        {body}"""
    with smtp.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:

        server.ehlo()

        server.starttls()

        server.login(config.USERNAME, config.PASSWORD)

        server.sendmail(sender, receiver, message)
