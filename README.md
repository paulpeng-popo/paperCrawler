# paperCrawler
A crawler for https://ndltd.ncl.edu.tw/ (臺灣碩博士論文加值系統)

1. Your will be assigned two numbers
2. Put them into captchaSolver/config.py `SCHOOLS`
3. Execute getPaper.py
4. Then you will start crawling


+ For example
  + I am assigned `76 ~ 81`
  + Then I change config.py `SCHOOLS` like this
```python
SCHOOLS = {
    ...
    "start": 76,
    "end": 81,
}
```
