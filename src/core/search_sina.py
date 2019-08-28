import multiprocessing
from bs4 import BeautifulSoup
import pandas as pd
import requests
import warnings
import bs4
import json

import csv
from src.core.title import get_title, get_pages
from src.core.kssum.run_submodular import get_summary

warnings.filterwarnings('ignore')

class GetSina(object):
    # 定义头文件，伪装成浏览器
    headers = {"User-Agent":
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}

    def get_url_sina(self, key):

        # key = '董明珠雷军新赌约'

        url = 'http://api.search.sina.com.cn/?c=news&q={}&stime=2018-08-25&etime=2019-08-27&sort=rel&highlight=1&num=10&ie=utf-8'.format(key)
        print(url, '\n')

        response = requests.get(url, headers=self.headers)
        try:
            text_json = json.loads(response.text.encode('utf-8'))
            content = text_json["result"]["list"]
        except:
            return False

        return content

    def get_text_sina(self, content):

        articles_url = list()
        articles_list = list()
        big_texts = list()

        #获取热点文章的URL, 并且解析热点文章
        for json_reponse in content:

            url = json_reponse["url"]
            response = requests.get(url, headers=self.headers)
            text = response.content.decode("utf-8")
            soup = BeautifulSoup(text, "html.parser")
            result = str(soup.find("div", id='artibody'))
            subsoup = BeautifulSoup(result, "html.parser")

            lines = []
            for item in subsoup.find_all('p'):
                if isinstance(item, bs4.element.Tag):
                    if item.name == "p":
                        if item.text:
                            lines.append(item.text)

            articles_url.append(url)
            articles_list.append(lines)

        #将文章分为四个部分, 分别对四个部分进行信息提取
        print(len(articles_list), len(articles_list[0]))

        num_parts = 4
        num_sentences = len(articles_list[0])
        step = num_sentences // num_parts

        for i in range(0, num_parts):
            big_texts.append(''.join([sentence for sentence in articles_list[0][step*i:step*(i+1)]]))

        return articles_url[0], articles_list[0], big_texts


if __name__ == '__main__':

    titles = list()
    html = get_title()
    get_pages(html)
    with open('../data/title.csv', 'r', encoding='utf-8') as csvFile:
        f_csv = csv.reader(csvFile)
        for row in f_csv:
            if row[1] != 'Title':
                titles.append(row[1])

    print(titles, '\n')
    title = titles[-2]
    print(title, '\n')

    sina = GetSina()
    content = sina.get_url_sina(title)

    if content:
        articles_url, articles_list, texts = sina.get_text_sina(content)
        print(articles_url, '\n')

        for text in texts:
            extract_text = get_summary(text, language='chinese', wlimit=150)
            extract_text = json.loads(extract_text, encoding=False)
            extract_sentences = extract_text['result']

            tmp = list()
            for sentence in extract_sentences:
                tmp.append(sentence['sentence'])

            print("".join(tmp), '\n')






# # 创建一个进程池 Pool
# pool = multiprocessing.Pool(multiprocessing.cpu_count())
#
# # 循环次数
# for num in range(0, 30):
#     pool.apply_async(geturl, (url, num, key)) # 多进程
# pool.close()
# # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数会等待所有子进程结束。
# pool.join()












