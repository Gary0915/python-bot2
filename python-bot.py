import os
import requests
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 設定Line Bot的Channel Access Token和Channel Secret
line_bot_api = LineBotApi('U1WInxZ0t325PAjM7LPyjbACWWxvrk9jyFeU+eC2JGipJ5cYK7xwM+Dm2gzSFgipG+ia5iIh8+sROBtOtpQISvm8Jax+il463PQLMer7iwPxsjS4zrKmzYGH2DjnIHgcarPfvMaSZsyj5RZo9sywOgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('Y6c4a6bbf5f9f762a7e231af8d1ce529f')

# 設定OpenAI API Key
openai.api_key = "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"
model_engine = "davinci"

@app.route("/", methods=['GET'])
def index():
    return "Hello World!"

@app.route("/callback", methods=['POST'])
def callback():
    # 取得Line Server發來的X-Line-Signature
    signature = request.headers['X-Line-Signature']

    # 取得Line Server發來的內容
    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)

    try:
        # 進行簽名驗證
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 當接收到使用者訊息時，進行相應的處理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    if text == '天氣':
        # 詢問使用者要查詢哪個地點的天氣
        reply_message = TextSendMessage(text='你想要查詢哪個地方的天氣？')
        line_bot_api.reply_message(event.reply_token, reply_message)

    elif text.startswith('天氣 '):
        # 取得地點
        location = text[3:]

        # 使用Weather API取得天氣資訊
        url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=CWB-ED00D339-4DA6-4032-AF4F-C7FC1B5481DE&units=metric'.format(location)
        response = requests.get(url)
        data = response.json()

        # 提取所需資訊
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']

        # 回覆使用者天氣資訊
        reply_message = TextSendMessage(text='{}目前的溫度為{}度，{}，風速為{}m/s。'.format(location, temperature, description, wind_speed))
        line_bot_api.reply_message(event.reply_token, reply_message)

    elif text == '問題':
        # 提示使用者輸入問題
        reply_message = TextSendMessage(text='請輸入你的問題。')
        line_bot_api.reply_message(event.reply_token, reply_message)

    else:
        # 回覆使用者訊息
        reply_message = TextSendMessage(text=event.message.text)
       
    # 使用OpenAI回答使用者問題
    prompt = "請回答以下問題：\n" + text
    response = openai.Completion.create(engine=model_engine, prompt=prompt, max_tokens=100)
    answer = response.choices[0].text.strip()

    # 回覆使用者答案
    reply_message = TextSendMessage(text=answer)
    line_bot_api.reply_message(event.reply_token, reply_message)

if __name__ == "__main__":
    app.run()