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

line_bot_api = LineBotApi('homxuLtutR1rFTe8601K7SaMt9uDLE/XS6YlG/JsELRc3qIV/FJkjOcvON6SHB3UarwRv5fDX6ZBWor3wjxOiLyIfxhDKrZQ7XDPCMX7wZjFF0S0rEZChy1sLxc3Pdev0kyWrZmCRXR0wEPyVPhanwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('679f52751009e82e61dd4e6a4c34af0e')


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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()