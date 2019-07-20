import base64
import hashlib
import hmac
import json
import threading
import time
import traceback

import websocket
import requests


API_KEY = ''
SECRET_KEY = ''
PASS_PHRASE = ''


def get_ws_token():
    url = 'https://api.kucoin.com/api/v1/bullet-private'
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'POST' + '/api/v1/bullet-private'
    signature = base64.b64encode(
        hmac.new(SECRET_KEY.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": API_KEY,
        "KC-API-PASSPHRASE": PASS_PHRASE
    }
    response = requests.request('post', url, headers=headers)
    return response.json()['data']['token']


def on_message(ws, message):
    try:
        # print(type(message), message)
        message = json.loads(message)

        if message['type'] == 'message':
            if message['subject'] == 'account.balance':
                print(message['data'])
            if message['subject'] == 'trade.l3received':
                print(message['data'], False)
            if message['subject'] == 'trade.l3match':
                print(message['data'], True)
            if message['subject'] == 'trade.l3done':
                print(message['data'], True)

    except KeyboardInterrupt:
        pass
    except:
        print(traceback.format_exc())


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print('### opened ###')

    def ping(ws):
        while True:
            now = int(time.time() * 1000)
            ws.send('{"id":"' + str(now) + '","type":"ping"}')
            time.sleep(50)

    th = threading.Thread(target=ping, kwargs={"ws": ws})
    th.start()


def launch():

    while True:
        print('Websocket running')
        time.sleep(.1)

        token = get_ws_token()
        print(token)

        try:
            ws = websocket.WebSocketApp(
                f"wss://push1-v2.kucoin.com/endpoint?token={token}&connectId=1&acceptUserMessage=true",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close)

            ws.run_forever()
        except:
            print('ws Error: websocket failed')
            print(traceback.format_exc())


if __name__ == '__main__':
    try:
        launch()
    except KeyboardInterrupt:
        exit()
