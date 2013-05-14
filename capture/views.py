from flask import render_template
from sqlalchemy.sql.expression import desc
from twilio.rest import TwilioRestClient

from capture import app
from capture.database import db_session
from capture.models import Message, Entries
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

import watch

twilio_client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.route("/", methods=["GET", "POST"])
def refresh():
    watch.go()
    messages = twilio_client.sms.messages.list()
    for message in messages:
        exists = Message.query.filter(Message.sid == message.sid).count()
        if not exists:
            message = Message(sid=message.sid,
                              date_time=message.date_sent,
                              sent=message.from_,
                              received=message.to,
                              body=message.body,
                              status=message.status,
                              direction=message.direction,
                              uri=message.uri)
            db_session.add(message)
            db_session.commit()
            entry = Entries(message_id=message.id,
                            date_time=message.date_time)
            db_session.add(entry)
            db_session.commit()
    entries = db_session.query(Entries).order_by(desc(Entries.date_time)).all()
    return render_template("views.html",
                           entries=entries)
