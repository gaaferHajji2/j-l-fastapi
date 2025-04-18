from config import config

import smtplib as smtp

sender = "Private Person <example@example.com>"
receiver = "A Test User <gaafer.hajji1995@gmail.com>"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtp.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:
    server.starttls()

    server.login(config.USERNAME, config.PASSWORD)

    server.sendmail(sender, receiver, message)

