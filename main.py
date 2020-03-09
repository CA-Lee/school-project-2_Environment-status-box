from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import re
import time
import os

import sqlalchemy

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

def get_Server_Status():
    
    res = "Server status:\n"
    res += "Now time: " + time.strftime("UTC%z %Y/%m/%d %T") + "\n"

    return res

db = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_pass,
        database=db_name,
        query={"unix_socket": "/cloudsql/{}".format(cloud_sql_connection_name)},
    ),
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,
)

@app.route("/")
def root():
    return "<center><h1>Hello GAE</h1></center>"
'''
    with db.connect() as conn:
        # Execute the query and fetch all results
        recent_votes = conn.execute(
            "SELECT * FROM main_db.app_log;"
        ).fetchall()

    return str(recent_votes)
'''



@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if re.search("^ping$", event.message.text, re.I):
        srv_status = get_Server_Status()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=srv_status)
        )
    else:
        autoreplytext='Command allowed now:\n- Ping'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Hello " + event.message.text + "\n\n" + autoreplytext)
        )

if __name__ == "__main__":
    app.run()