# -*- coding:utf-8 -*-
'''
读关键词文件，然后百度搜索到关键词前30页的url爬取并保存至MOngoDB
'''
import multiprocessing  # 利用pool进程池实现多进程并行
from bs4 import BeautifulSoup  # 处理抓到的页面
import requests
import warnings

import time
import urllib3
import logging
import re

from scrapy.http.response import html
from urllib.parse import quote

import csv
from src.core.search_title import get_title
import urllib

# 忽略警告
warnings.filterwarnings('ignore')

# 定义头文件，伪装成浏览器
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-US,en;q=0.9',
           'Cookie': 'UOR=www.google.com,news.sina.com.cn,; '
                     'SINAGLOBAL=34.97.198.83_1566526935.526570;'
                     ' Apache=34.97.198.83_1566526935.526571;'
                     ' lxlrttp=1560672234;'
                     ' ULV=1566526944749:2:2:2:34.97.198.83_1566526935.526571:1566526935142;'
                     ' U_TRS1=00000053.4db07522.5d5f4de1.a0cdc576;'
                     ' U_TRS2=00000053.4db87522.5d5f4de1.e1353bd4;'
                     ' SUB=_2AkMqA8LOf8NxqwJRmfgSyG3hZI52yg3EieKcXzMVJRMyHRl-yD83qlMZtRB6AYPsIZIXjG5SO3UO25lg-2VaHXtM2HTf;'
                     ' SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWRJqWOMbpV88vDjESWxim3;'
                     ' SGUID=1566526990117_58244411;'
                     ' UM_distinctid=16cbc49b8c19f8-06c34546347f58-3f75065b-1fa400-16cbc49b8c28a3;'
                     ' CNZZDATA5832809=cnzz_eid%3D1659869561-1566543513-%26ntime%3D1566543513;'
                     ' CNZZDATA1271230489=823908648-1566522306-%7C1566543906',
           'Host': 'www.sina.com.cn',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

def getfromSina(key):

    # url = 'http://www.baidu.com.cn/s?wd=' + urllib.parse.quote(key) + '&pn='  # word为关键词，pn是分页。
    url = 'http://www.sina.com.cn/mid/search.shtml?range=all&c=news&q=' + urllib.parse.quote(key) + '&from=home&ie=utf-8'  # word为关键词，pn是分页。
    req = requests.get(url, verify=False, headers=headers, timeout=5)
    response = html.HtmlResponse(encoding='utf-8', url=url, headers=headers, body=req.content)

    links = response.xpath('//div[@id="content_left"]/div[@class="result c-container "]/h3/a/@href').extract()
    print(links)


    # soup = BeautifulSoup(response.text, 'lxml')
    # tagh3 = soup.find_all('box-result clearfix')
    # print(tagh3)
    exit()

    # 创建一个进程池 Pool
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    # 循环次数
    for num in range(0, 30):
        pool.apply_async(geturl, (url, num, key)) # 多进程
    pool.close()
    # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数会等待所有子进程结束。
    pool.join()


def geturl(url, num, key):

    path = url + str(num * 10)
    response = requests.get(path, timeout=5)
    soup = BeautifulSoup(response.text, 'lxml')
    tagh3 = soup.find_all('h3')

    real_urls = list()
    for h3 in tagh3:
        href = h3.find('a').get('href')
        baidus_url = requests.get(url=href, headers=headers, allow_redirects=False)
        real_url = baidus_url.headers['Location']  # 得到网页原始地址
        real_urls.append(real_url)
        print(real_url)
    return real_urls


if __name__ == '__main__':

    titles = list()
    get_title()
    with open('../data/title.csv', 'r', encoding='utf-8') as csvFile:
        f_csv = csv.reader(csvFile)
        for row in f_csv:
            if row[1] != 'Title':
                titles.append(row[1])

    key = titles[0]
    real_urls = getfromSina(key)
    print(real_urls)










































