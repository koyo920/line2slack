import os

import requests
import slackweb
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage

app = Flask(__name__)

# heroku config:set LINE_CHANNEL_ACCESS_TOKEN=C6HvXpZ/biiV1QHrzLeQTWFPVhZo4kICW8s7bSFRbFG5Oo4irGEGx8Gmx+TResYLTQLYXcBKHeSW+FCVZ7NuF4FBjWPxoOFwRalf3sCCx64a0PxVQVi/DtrVVmjXorYy1EFtTkBGgR8MhuxuHZ0ssgdB04t89/1O/w1cDnyilFU= --app line2nombey
# heroku config:set LINE_CHANNEL_SECRET=60778b49be8dd61d2537eb1e616e0bfb --app line2nombey
# heroku config:set SLACK_WEB_HOOKS_URL=https://hooks.slack.com/services/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 --app line2nombey

# 認証情報の取得
CHANNEL_ACCESS_TOKEN = os.environ.get["BIDIMTF3bcJZl86K9h2iy9H8BZQf+E0jz5so+L0cXNvbvjTxTa4FiK0bOi40Ra9M8q+CI32ROyHFxIejnosFjQlz/7IFRytCxYkWs2ftI6EKxInc5ONHcH988+YlcsWGcxXQLRK2yIjf2O5JzWEVqgdB04t89/1O/w1cDnyilFU="]
CHANNEL_SECRET = os.environ.get["60778b49be8dd61d2537eb1e616e0bfb"]
WEB_HOOK_LINKS = os.environ.get["https://hooks.slack.com/services/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"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", method=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle web hook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def get_event_info(event):
    """
    トーク情報の取得
    :param event: LINE メッセージイベント
    :return: ユーザID, ユーザ表示名, 送信元トークルームの種別, ルームID
    :rtype: str, str, str, str
    """

    # LINEユーザー名の取得
    user_id = event.source.user_id
    try:
        user_name = line_bot_api.get_profile(user_id).display_name
    except LineBotApiError as e:
        user_name = "Unknown"

    # トーク情報の取得
    if event.source.type == "user":
        msg_type = "個別"
        room_id = None
        return user_id, user_name, msg_type, room_id

    if event.source.type == "group":
        msg_type = "グループ"
        room_id = event.source.group_id
        return user_id, user_name, msg_type, room_id

    if event.source.type == "room":
        msg_type = "複数トーク"
        room_id = event.source.room_id
        return user_id, user_name, msg_type, room_id


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """
    Text Message の処理
    """
    slack_info = slackweb.Slack(url=WEB_HOOK_LINKS)

    # トーク情報の取得
    user_id, user_name, msg_type, room_id = get_event_info(event)

    # slack側に投稿するメッセージの加工
    send_msg = "[bot-line] {user_name}さん\n".format(user_name=user_name) \
               + "{msg}\n".format(msg=event.message.text) \
               + "---\n" \
               + "送信元: {msg_type} ( {room_id} )\n".format(msg_type=msg_type, room_id=room_id) \
               + "送信者: {user_name} ( {user_id} )".format(user_name=user_name, user_id=user_id)

    # メッセージの送信
    slack_info.notify(text=send_msg)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)