import time
from datetime import datetime

import requests
from alive_progress import alive_bar
from bs4 import BeautifulSoup
from config import *


def setWebSession() -> dict:
    """
    set web session
    """

    # create session
    session = requests.Session()
    url = "https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/login?o=dwebmge"

    # get session cookies
    try:
        r = session.get(url, headers=HEADERS)
        cookies = session.cookies.get_dict()
        if "ccd" not in cookies:
            print("Failed to get cookies.")
            print("Please check your internet connection.")
            print("If you are using VPN, please turn it off.")
            exit(1)
        return session, cookies['ccd']
    except Exception as e:
        print("Error: {}".format(e))
        print("Failed to get cookies.")
        exit(1)


def getCaptcha(session: requests.Session, ccd: str) -> None:

    # get time stamp
    timeStamp = datetime.timestamp(datetime.now())
    cache = int(timeStamp * 1000)

    base_url = "https://ndltd.ncl.edu.tw"
    url = "https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd={}".format(ccd)
    url += "/dispcheckimg_ajax?&cache={}".format(cache)

    request = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(request.text, "html.parser")
    img = soup.find("img")
    img_url = img["src"]

    # get captcha image
    request = session.get(base_url + img_url, headers=HEADERS)
    with open(DataPath.format(cache), "wb") as f:
        f.write(request.content)


if __name__ == "__main__":
    session, ccd = setWebSession()

    with alive_bar(DataSetSize, bar="smooth", spinner="classic", title="Getting Captcha Data") as bar:
        for i in range(DataSetSize):
            getCaptcha(session, ccd)
            bar()
            time.sleep(1)
