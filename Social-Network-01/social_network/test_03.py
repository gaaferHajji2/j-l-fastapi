from config import config

import smtplib as smtp

sender = "Private Person <gaafer.hajji1995@gmail.com>"
receiver = "A Test User <larkinjoe753@gmail.com>"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtp.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:

    server.ehlo()

    server.starttls()

    server.login(config.USERNAME, config.PASSWORD)

    server.sendmail(sender, receiver, message)

