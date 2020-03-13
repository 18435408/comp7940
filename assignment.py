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

app = Flask(__name__)

line_bot_api = LineBotApi('KtaPsfYdXzLDUGMfgRFH7kmNQL8PRItuyeNnQiMZt2TgzC1Fs/J5ju0qmz4BgabgMFn+Qmr1lDTg/0ciUAp8WK5dygUBwqY3YTaFK3HaTS+YT+0ayrHQisaaww631nsoh7He5S28pVIfhQEfazXA0AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9b585f0cbb929b5d982f92f6119cb81b')

      
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=80)