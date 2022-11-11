# paperCrawler speed up version
A crawler for https://ndltd.ncl.edu.tw/ (臺灣碩博士論文加值系統)

1. Your should have gotten two numbers from 逸翔
2. Put them into captchaSolver/config.py `SCHOOLS`
3. Execute getPaper.py in the project root
4. Then you will start crawling


## Note:
+ If you have already crawled something but is not done yet
+ Just move them into the project root same with getPaper.py
+ And simply execute getPaper.py for continue

## For example
  + I am assigned `76 ~ 81`
  + Then I change config.py `SCHOOLS` like this
```python
SCHOOLS = {
    ...
    "start": 76,
    "end": 81,
}
```
