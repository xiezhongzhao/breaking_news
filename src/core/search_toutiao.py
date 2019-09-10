# !/usr/bin/env python
# encoding: utf-8
#
# @Author: Xie Zhongzhao
# @Date  : 2019-09-02 10:12:00

from urllib.parse import urlencode
import requests
from requests.exceptions import RequestException
import json
import time
import re

# def get_page_index(offset, keyword):
#
#     headers = {"accept" : "application/json, text/javascript",
#                "user-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
#                "cookie" : "tt_webid=6728261370234930700; WEATHER_CITY=%E5%8C%97%E4%BA%AC; "
#                           "csrftoken=a506930f88921098e5c8552da61bac24; tt_webid=6728261370234930700; "
#                           "s_v_web_id=cabf03df2a095acc7c641bef15039b98; __tasessionId=ybvqu8p7t1568010919114"}
#
#     data={
#         'aid' : '24',
#         'app_name' : 'web_search',
#         'offset' : offset,
#         'format' : 'json',
#         'keyword' : keyword,
#         'autoload' : 'true',
#         'count' : '20',
#         'en_qc' : '1',
#         'cur_tab' : '1',
#         'from' : 'search_tab',
#         'pd' : 'synthesis',
#         'timestamp' : '1568105415728'
#     }
#
#     url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
#
#     try:
#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             return response.text.encode('utf-8')
#         return None
#
#     except RequestException:
#         print("请求失败")
#         return None
#
# def parse_page_index(html):
#
#     article_urls = list()
#     results = json.loads(html)
#     if results and 'data' in results.keys():
#         for item in results.get('data'):
#             try:
#                 # yield item.get('article_url')
#                 article_urls.append(item.get('article_url'))
#                 time.sleep(0.5)
#             except:
#                 continue
#
#         toutiao_urls = list()
#         for url in article_urls:
#
#             try:
#                 if url.startswith('http://toutiao.com/'):
#                     toutiao_urls.append(url)
#             except:
#                 continue
#
#         return toutiao_urls
#
#     return None
#
#
# def parse_page_detail(html):
#
#     pass
#
#
# def main():
#     html = get_page_index(0, '广汽本田出新车')
#     toutiao_urls = parse_page_index(html)
#     print(toutiao_urls)
#
#
# if __name__ == '__main__':
#     main()



from bs4 import BeautifulSoup
headers = {"accept" : "application/json, text/javascript",
               "user-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
               "cookie" : "tt_webid=6728261370234930700; WEATHER_CITY=%E5%8C%97%E4%BA%AC; "
                          "csrftoken=a506930f88921098e5c8552da61bac24; tt_webid=6728261370234930700; "
                          "s_v_web_id=cabf03df2a095acc7c641bef15039b98; __tasessionId=ybvqu8p7t1568010919114"}

url = 'https://www.toutiao.com/a6729656773487100429/'

response = requests.get(url, headers=headers)
response.encoding = response.apparent_encoding
response = response.text

soup = BeautifulSoup(response, 'lxml')
title = soup.select('title')[0].get_text()
print(title)

# content_pattern = re.compile('(var BASE_DATA.*\<\/script\>)?')
content_pattern = re.compile('<script>.*?</script>')
result = re.search(content_pattern, response)
if result:
    print(result.group(0))










