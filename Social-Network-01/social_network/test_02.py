import mailtrap as mt

from config import config

# This WillNot Work, Because We Need HTTPS Request.
# And, Python Doesn't Support Sandbox Email Sending

mail = mt.Mail(
    sender=mt.Address(email="example@example.com"),
    to=[mt.Address(email="gaafer.hajji1995@gmail.com")],
    subject="For Testing Only",
    text="This Is For Testing Sending Emails"
)

client = mt.MailtrapClient(token=config.API_KEY)

try:
    client.send(mail=mail)
except mt.exceptions.AuthorizationError as e:
    print(e.errors)

print("Success")