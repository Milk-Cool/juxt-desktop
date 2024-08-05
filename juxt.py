"""See README.md"""


from mitmproxy import http
from mitmproxy import ctx
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "PretendoClients"))
from nintendo import nnas
from base64 import b64encode

import logging
logging.basicConfig(level=logging.INFO)

TITLE_ID = 0x000500301001600A
TITLE_VERSION = 0

DEVICE_ID = int(os.environ["DEVICE_ID"])
SERIAL_NUMBER = os.environ["SERIAL_NUMBER"]
SYSTEM_VERSION = int(os.environ["SYSTEM_VERSION"], 16)
REGION_ID = int(os.environ["REGION_ID"])
COUNTRY_NAME = os.environ["COUNTRY_NAME"]
LANGUAGE = os.environ["LANGUAGE"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
CERT = os.environ["CERT"]

async def token():
    global DEVICE_ID, SERIAL_NUMBER, SYSTEM_VERSION, CERT
    global TITLE_ID, TITLE_VERSION
    global REGION_ID, COUNTRY_NAME, LANGUAGE
    global USERNAME, PASSWORD
    try:
        nas = nnas.NNASClient()
        nas.set_device(DEVICE_ID, SERIAL_NUMBER, SYSTEM_VERSION, CERT)
        nas.set_title(TITLE_ID, TITLE_VERSION)
        nas.set_locale(REGION_ID, COUNTRY_NAME, LANGUAGE)

        access_token = await nas.login(USERNAME, PASSWORD)
        service_token = await nas.get_service_token(access_token.token, "87cd32617f1985439ea608c2746e4610")

        return service_token
    except Exception as e:
        print(f"Server {hex(TITLE_ID)} down!")
        logging.exception(e)
        return False

TOKEN = False
lock = False

class JuxtAddon:
    def load(_self, _loader):
        ctx.options.http2 = False
        ctx.options.ssl_insecure = True

    async def request(_self, flow: http.HTTPFlow) -> None:
        global TOKEN, lock
        if not TOKEN:
            if lock:
                return
            lock = True
            TOKEN = await token()
            ctx.log.info("Token: " + TOKEN)
            if not TOKEN:
                exit(1)
            lock = False
        if "portal.olv.pretendo.cc" == flow.request.host:
            flow.request.headers["X-Nintendo-ParamPack"] = b64encode(bytes("\\language_id\\1\\platform_id\\1\\country_id\\1\\region_id\\" + str(REGION_ID) + "\\", "utf-8"))
            flow.request.headers["X-Nintendo-ServiceToken"] = TOKEN
            flow.request.headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            flow.request.headers["accept-encoding"] = "gzip, deflate"
            flow.request.headers["accept-language"] = LANGUAGE
            if flow.request.method == "POST":
                flow.request.headers["content-type"] = "application/x-www-form-urlencoded"
            # flow.request.headers["host"] = "portal.olv.pretendo.cc"
            # flow.request.headers["origin"] = "https://portal.olv.pretendo.cc"
        flow.request.headers["user-agent"] = "Mozilla/5.0 (Nintendo WiiU) AppleWebKit/536.28 (KHTML, like Gecko) NX/3.0.3.12.6 miiverse/3.1.prod.JP"

addons = [JuxtAddon()]