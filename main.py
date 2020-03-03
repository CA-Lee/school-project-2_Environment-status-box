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

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

line_bot_api = LineBotApi(app.config.get('YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(app.config.get('YOUR_CHANNEL_SECRET'))

def get_Server_Status():
    
    res = "Server status:\n"
    res += "Now time: " + time.strftime("UTC%z %Y/%m/%d %T") + "\n"

    return res

@app.route("/")
def root():
    return "<center><h1>Hello GAE</h1></center>"

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