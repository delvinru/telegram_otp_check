"""
Module for request from web page to base64 encoded string
"""
import asyncio
import io
from base64 import b64encode

import qrcode
import websockets

import lib.util
from lib.settings import BOT_URL


async def update_otp_code(websocket, path):
    """Function run in Thread and update otp_code variable"""

    while True:
        data = BOT_URL + lib.util.otp_code
        img = qrcode.make(data).get_image()
        out = io.BytesIO()
        img.save(out, 'png')

        prefix = "data:image/png;base64,"
        raw_data = b64encode(out.getvalue()).decode()
        data = prefix + raw_data
        try:
            await websocket.send(data)
        except websockets.exceptions.ConnectionClosedOK:
            break
        except websockets.exceptions.ConnectionClosedError:
            break

        await asyncio.sleep(3)

def start_websocket():
    """Init websocket server for exchanging data"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    HOST, PORT = "0.0.0.0", 9999
    srv = websockets.serve(update_otp_code, HOST, PORT)

    asyncio.get_event_loop().run_until_complete(srv)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    start_websocket()
