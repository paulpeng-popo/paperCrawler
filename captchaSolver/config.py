import os

SCHOOLS = {
    "path": os.path.join(os.path.dirname(__file__), "../school.csv"),
    "encoding": "utf-8",
    "delimiter": ",",
    "mode": "r",
    "start": 76,
    "end": 81,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

DataPath = os.path.join(os.path.dirname(__file__), "data", "{}.jpg")
DataSetSize = 100

DataSetPath = os.path.join(os.path.dirname(__file__), "data")
TestPath = os.path.join(os.path.dirname(__file__), "test")
