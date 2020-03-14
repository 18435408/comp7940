from flask import Flask, request, abort
from urllib.request import urlopen, Request
import key
from io import StringIO
import pandas as pd
import requests
import redis
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

r = redis.Redis(host='localhost', port=6379, db=0)
      
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
                            label='Record Temperature',
                            text='@record'
                        ),
                        MessageAction(
                            label='Where can buy Mask',
                            text='@whereBuySurgicalMask'
                        ),
                        MessageAction(
                            label='Latest Status',
                            text='@latestInformation'
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
                            label='Personal Advice',
                            text='@advice'
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

        elif event.message.text.startswith("@record"):
            data = event.message.text.split(" ")
            if len(data) != 2:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Please record your temperature using `@record Temperature` Format.\nEg. @record 36.5 \n\nFor showing history, use @showRecords")
                )
            else:
                try:
                    temp = float(data[1])
                    r.set('lastTemp-'+event.source.user_id, temp)
                    if temp > 37.5:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="Your Temperature is "+str(temp) +" , seem to be having a fever. Please contact docter whenever possible.")
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="Record Temperature "+str(temp) +" Successfully.")
                        )
                except ValueError:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="Invalid Input.\nPlease record your temperature using `@record Temperature` Format.\nEg. @record 36.5 \n\nFor showing history, use @showRecords")
                    )
        elif event.message.text =="@latestInformation":
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
            url="http://www.chp.gov.hk/files/misc/enhanced_sur_pneumonia_wuhan_eng.csv"
            s=requests.get(url, headers= headers).text
            c=pd.read_csv(StringIO(s), sep=",")
            genders = c.groupby("Gender")
            status = c.groupby("Hospitalised/Discharged/Deceased")
            residents = c.groupby("HK/Non-HK resident")
            cases = c.groupby("Case classification*")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Latest Status : \n\nTotal Cases : "+str(len(c))+"\nMale : "+str(len(genders.get_group("M")))+" Female : "+str(len(genders.get_group("F")))+"\nHospitalised : "+str(len(status.get_group("Hospitalised")))+"\nDischarge : "+str(len(status.get_group("Discharged")))+"\nDeceased : "+str(len(status.get_group("Deceased")))+"\nHK resident : "+str(len(residents.get_group("HK resident")))+"\nNon-HK resident : "+str(len(residents.get_group("Non-HK resident")))+"\nImported : "+str(len(cases.get_group("Imported")))+"\nClose contact of imported case : "+str(len(cases.get_group("Close contact of imported case")))+"\nPossibly local : "+str(len(cases.get_group("Possibly local")))+"\nClose contact of possibly local case : "+str(len(cases.get_group("Close contact of possibly local case")))+"")
            )

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="To view command list , Type @help \U001000AE . Stay safe and take care, always wash hands.")
            )

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=80)