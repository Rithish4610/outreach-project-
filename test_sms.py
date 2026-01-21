from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

client.messages.create(
    body="Test SMS from clinic project",
    from_=os.getenv("TWILIO_PHONE"),
    to="+919363613681"
)

print("Done")
