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
import googlemaps
from random import sample
import requests

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
#provide googlemaps key
def gmaps_key():
    gmaps = googlemaps.Client(key='AIzaSyBxPxGKE7btQHErpX044ZAnf40bFDLEU6I')
    return gmaps

#find latitude and longitude
def find_lat_lng():
    address = input('請輸入地址: ')
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=AIzaSyBxPxGKE7btQHErpX044ZAnf40bFDLEU6I')
    resp_json_payload = response.json()
    result_lat_lng = resp_json_payload['results'][0]['geometry']['location']
    result_lat_lng = str([result_lat_lng['lat'], result_lat_lng['lng']]).strip('[]')
    return result_lat_lng

#find stores nearby by my house
def find_nearby_all_results(gmaps, result_lat_lng):
    keyword = input('請輸入搜尋類別or關鍵字: ')
    radius = int(input('請輸入搜尋範圍(m): '))
    places_results = gmaps.places_nearby(location=result_lat_lng, radius=radius, keyword=keyword)
    places_results = places_results['results']
    return places_results

#add filters: rating & user rating total
def find_nearby_after_filter(places_results):
    input_rating = float(input('請輸入google評分至少幾顆星: '))
    input_rating_total = float(input('請輸入google評分至少幾個人評分: '))
    goal_results = []
    for places_result in places_results:
        name = places_result['name']
        rating = float(places_result['rating'])
        user_ratings_total = float(places_result['user_ratings_total'])
        if rating >= input_rating and user_ratings_total >= input_rating_total :
            goal_results.append(name)
    return goal_results


def print_results(goal_results):
    r = sample(goal_results,2)


def main():
    gmaps = gmaps_key()
    result_lat_lng = find_lat_lng()
    places_results = find_nearby_all_results(gmaps, result_lat_lng)
    goal_results = find_nearby_after_filter(places_results)
    print_results(goal_results)


def handle_message(event):
    msg = event.message.text
    r = '請輸入搜尋地址: '

    if '區' in msg:
        address = msg
        r = '請輸入搜尋類別or關鍵字: '
    elif ('餐廳' or '飲料') in msg:
        keyword = msg
        r = '請輸入搜尋範圍(m): '
    elif '00' in msg:
        radius = int(msg)
        r = '請輸入google評分至少幾顆星(小數點後一位): '
    elif '.' in msg:
        rating = float(msg)
        r = '請輸入google評分至少幾個人評分(數字51結尾): '
    elif '51' in msg:
        input_rating_total = float(msg)
        main()

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=r))


if __name__ == "__main__":
    app.run()