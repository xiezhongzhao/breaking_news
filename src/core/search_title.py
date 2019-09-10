#!/usr/bin/env python
# encoding: utf-8

# @Author: Xie Zhongzhao
# @Date  : 2019-09-02 10:12:00

import requests
from bs4 import BeautifulSoup
import csv

def get_title(url):

    headers = {'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, image/webp, image/apng, */*;q=0.8, application/signed-exchange; v = b3',
               'Accept-Encoding' : 'gzip, deflate',
               'Accept-Language': 'en-US, en; q=0.9',
               'Connection': 'keep-alive',
               'Host': 'top.baidu.com',
               'User-Agent': 'Mozilla/5.0'}

    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    return r.text

def get_pages(html, csv_file):

   soup = BeautifulSoup(html,'html.parser')
   all_topics=soup.find_all('tr')[1:]

   writer = csv.writer(csv_file)
   fileHeader = ["Rank", "Title", "Hit_"]
   writer.writerow(fileHeader)

   for each_topic in all_topics:
       topic_times = each_topic.find('td', class_='last')  # 搜索指数
       topic_rank = each_topic.find('td', class_='first')  # 排名
       topic_name = each_topic.find('td', class_='keyword')  # 标题目

       if topic_rank != None and topic_name != None and topic_times != None:
           topic_rank = each_topic.find('td', class_='first').get_text().replace(' ', '').replace('\n', '')
           topic_name = each_topic.find('td', class_='keyword').get_text().replace(' ', '').replace('\n', '').replace('search','')
           topic_times = each_topic.find('td', class_='last').get_text().replace(' ', '').replace('\n', '')

           title_list = list()
           title_list.append(topic_rank)
           title_list.append(topic_name)
           writer.writerow(title_list)

# test part
if __name__ == '__main__':

    #百度热点排行榜单链接
    urls = [
        'http://top.baidu.com/buzz?b=1&fr=20811',  # 实时热点
        'http://top.baidu.com/buzz?b=341&c=513&fr=topbuzz_b42_c513', # 今日热点
        'http://top.baidu.com/buzz?b=42&c=513&fr=topbuzz_b1679_c513', # 七日热点
        'http://top.baidu.com/buzz?b=342&c=513&fr=topbuzz_b342_c513', # 民生热点
        'http://top.baidu.com/buzz?b=344&c=513&fr=topbuzz_b11_c513', # 娱乐热点
        'http://top.baidu.com/buzz?b=11&c=513&fr=topbuzz_b1_c513' # 体育热点
    ]

    with open("../data/title.csv", 'w', encoding='utf-8') as csv_file:
        for url in urls:
            html = get_title(url)
            get_pages(html, csv_file)

    with open('../data/title.csv', 'r', encoding='utf-8') as csvFile:
        titles = list()
        f_csv = csv.reader(csvFile)
        for row in f_csv:
            if row[1] != 'Title':
                titles.append(row[1])

    print(titles)


































