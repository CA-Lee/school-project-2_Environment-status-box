from flask import Flask, request, abort, render_template

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
import datetime
import os

import sqlalchemy

app = Flask(__name__, static_url_path='')

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

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

keylist = ["source","brightness","t","h"]

@app.route("/")
def root():
    return "<center><h1>Hello GAE</h1></center>"

### Arduino ###

@app.route("/arduino_entry", methods=['POST'])
def arduino_entry():
    with db.connect() as conn:
        conn.execute("INSERT INTO `main_db`.`app_log` (`content`) VALUES ('/arduino_entry has been accessed at " + time.strftime("UTC%z %Y/%m/%d %T") + "');")
        
        keys = ""
        values = ""
        for k in keylist:
            if keys != "":
                keys += ", "
                values += ", "
            keys += "`" + k + "`"
            values += "'" + str(request.values.get(k)) + "'"

        conn.execute("INSERT INTO `main_db`.`sensor_data` (" + keys + ") VALUES (" + values + ");")
    return 'OK'

@app.route("/arduino_test")
def arduino_test():
    return render_template(
        "testpage.html", 
        keys=keylist
        )
@app.route("/sensor_data")
def sensor_data():
    
    with db.connect() as conn:
        # Execute the query and fetch all results
        data = conn.execute(
            "SELECT * FROM main_db.sensor_data ORDER BY timestamp desc limit 1;"
        )
        raw_timestamps = conn.execute("SELECT timestamp FROM main_db.sensor_data where source='MKR1000' ORDER BY timestamp desc limit 500;").fetchall()
        timestamps = [row[0].strftime("%X") for row in raw_timestamps]
        timestamps.reverse()
        raw_brightnesses = conn.execute("SELECT brightness FROM main_db.sensor_data where source='MKR1000' ORDER BY timestamp desc limit 500;").fetchall()
        brightnesses = [row[0] for row in raw_brightnesses]
        brightnesses.reverse()
        return render_template(
            "sensor_data.html", 
            keys=data.keys(),
            vals=data.fetchone(),
            timestamps=timestamps,
            brightnesses=brightnesses
        )

### Line Bot ###

def get_Server_Status():
    
    res = "Server status:\n"
    res += "Now time: " + time.strftime("UTC%z %Y/%m/%d %T") + "\n"

    return res

def get_newest_data():

    res = ""
    with db.connect() as conn:
        res = "The newest data:\n"
        sql_r = conn.execute("SELECT * FROM main_db.sensor_data ORDER BY timestamp desc limit 1;")
        col = (sql_r.keys(),sql_r.fetchone())
        res += str(col[0][0]) + " : " + str(col[1][0] + datetime.timedelta(hours=8)) + "\n"
        for i in range(1,len(col[0])):
            res += str(col[0][i]) + " : " + str(col[1][i]) + "\n"
    return res

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
    reply = ""
    
    if re.search("^ping$", event.message.text, re.I):
        reply = get_Server_Status()
    elif re.search("^get[\s_]now$", event.message.text, re.I):
        reply = get_newest_data()
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()