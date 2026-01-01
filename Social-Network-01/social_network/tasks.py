import logging
import smtplib as smtp

from social_network.config import config

logger = logging.getLogger(__name__)
# print(__name__)

async def send_simple_email(to: str, subject: str, body: str, from_: str):
    sender = f"Private Person <{from_}>"
    receiver = f"A Test User <{to}>"
    logger.debug(f"The Sender Is: {sender}")
    logger.debug(f"The Receiver Is: {receiver}")
    logger.debug(f"The Subject Is: {subject}")
    logger.debug(f"The Body Is: {body}")

    message = f"""\
Subject: {subject}
To: {receiver}
From: {sender}

{body}
"""
    
    logger.debug(f"The Complete Msg Is: {message}")
    with smtp.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(config.USERNAME, config.PASSWORD)
        result = server.sendmail(sender, receiver, message)
        logger.debug(f"The Result Of Sending Email Is: {result}")

async def send_user_registeration_email(email: str, confirmation_url: str):
    return await send_simple_email(
        to=email,
        subject="Please Confirm Your Email Address",
        body=f"Please Confirm Your Email Address Using This Link: {confirmation_url}",
        from_="gaafer.hajji1995@gmail.com"
    )
