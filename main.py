import os

import requests, json
import slackweb
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, ImageMessage

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ["C6HvXpZ/biiV1QHrzLeQTWFPVhZo4kICW8s7bSFRbFG5Oo4irGEGx8Gmx+TResYLTQLYXcBKHeSW+FCVZ7NuF4FBjWPxoOFwRalf3sCCx64a0PxVQVi/DtrVVmjXorYy1EFtTkBGgR8MhuxuHZ0ssgdB04t89/1O/w1cDnyilFU="]
CHANNEL_SECRET = os.environ["60778b49be8dd61d2537eb1e616e0bfb"]
WEB_HOOK_LINKS = os.environ["https://hooks.slack.com/services/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"]
BOT_OAUTH = os.environ["xoxb-479740998288-3188861833653-0lQq610NxDVvEvI2BzoQM0BP"]
POST_CHANNEL_ID = os.environ["C035JRRDFGD"]
USER_OAUTH = os.environ["SLACK_USER_OAUTH"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
### 以下省略 ###

# image file
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """
    Image Message
    """
    
    #get talk
    user_id, user_name, msg_type, room_id = get_event_info(event)

    #send lineImage recieve
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    img = message_content.content #画像データ
    # img = "/Users/okawarayu/Desktop/py_line_slack/sp_test_height.JPG"

    #slack
    send_msg = "[bot-line] {user_name} 画像を送信．\n".format(user_name=user_name) \
               + "---\n" \
               + "送信元: {msg_type} ( {room_id} )\n".format(msg_type=msg_type, room_id=room_id) \
               + "送信者: {user_name} ( {user_id} )".format(user_name=user_name, user_id=user_id)

    file_name = "send_image_{message_id}".format(message_id=message_id)
    
    # getimg = requests.get(img)
    # pillowimg = Image.open(BytesIO(getimg.content))
    # flipped_img = ImageOps.flip(pillowimg)
    # flipped_img.show()

    #send image
    url = 'https://slack.com/api/files.upload'
    headers = {"Authorization" : "Bearer "+ USER_OAUTH}
    files = {'file': img}
    param = {
        'user': user_id,
        # 'token': BOT_OAUTH,
        'channels': POST_CHANNEL_ID,
        'filename': file_name,
        'initial_comment': send_msg,
        'title': file_name,
    }
    print("!!! send slack log !!!", param)
    res = requests.post(url, params=param, files=files, headers=headers)
    print("res", res.json())