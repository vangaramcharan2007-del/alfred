"""
Outbound Telugu AI Voice Call to Dakshith via Twilio Carrier Bridge.
"""

import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")
from_num = os.getenv("TWILIO_PHONE_NUMBER")
to_num = "+918712484963"

client = Client(sid, token)

telugu_speech = (
    "నమస్కారం దక్ష్షిత్ గారు, నేను చరణ్ పర్సనల్ ఏఐ అసిస్టెంట్ ఆల్ఫ్రెడ్ ని మాట్లాడుతున్నాను. "
    "చరణ్ మిమ్మల్ని అర్జెంట్ గా కాంటాక్ట్ చేయమన్నారు. మీరు ఎలా ఉన్నారు?"
)

# TwiML for Telugu voice synthesis
twiml_payload = f"""<Response>
    <Say language="te-IN">{telugu_speech}</Say>
    <Pause length="1"/>
    <Say language="te-IN">ధన్యవాదాలు దక్ష్షిత్ గారు, చరణ్ కి ఈ మెసేజ్ చేరవేస్తున్నాను.</Say>
</Response>"""

print(f"[*] Initiating Telugu Carrier Voice Call to Dakshith ({to_num})...")
print(f"[*] From: {from_num}")

try:
    call = client.calls.create(
        twiml=twiml_payload,
        from_=from_num,
        to=to_num
    )
    print(f"\n[OK] CALL INITIATED SUCCESSFULLY!")
    print(f"  [+] Call SID : {call.sid}")
    print(f"  [+] Status   : {call.status}")
    print(f"  [+] Language : Telugu (te-IN)")
except Exception as e:
    print(f"\n[!] Twilio Gateway Response: {e}")
