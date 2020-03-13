from flask import Flask, request, abort

import key
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction
)

app = Flask(__name__)

line_bot_api = LineBotApi(key.key)
handler = WebhookHandler(key.secret)

      
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
        if event.message.text =="@help":
            help_message = TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='Command List',
                    text='Please Select:',
                    actions=[
                        MessageAction(
                            label='Where can buy Mask',
                            text='@whereBuySurgicalMask'
                        ),
                        MessageAction(
                            label='Latest Status',
                            text='@latestInformation'
                        ),
                        MessageAction(
                            label='Personal Advice',
                            text='@advice'
                        ),
                        MessageAction(
                            label='More',
                            text='@help2'
                        )
                    ]
                )
            )

            line_bot_api.reply_message(
                event.reply_token, help_message
            )
        elif event.message.text =="@help2":
            help_message = TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='Command List',
                    text='Please Select:',
                    actions=[
                        MessageAction(
                            label='Symptoms',
                            text='@symptoms'
                        ),
                        MessageAction(
                            label='Contact Numbers',
                            text='@contact'
                        ),
                        MessageAction(
                            label='Back',
                            text='@help'
                        )
                    ]
                )
            )

            line_bot_api.reply_message(
                event.reply_token, help_message
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="To view command list , Type @help \U001000AE . Stay safe and take care, always wash hands.")
            )

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=80)