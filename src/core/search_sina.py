import multiprocessing
from bs4 import BeautifulSoup
import requests
import warnings
import bs4
import json

import csv
from src.core.title import get_title

warnings.filterwarnings('ignore')

# 定义头文件，伪装成浏览器
headers = {"User-Agent":
           "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}

def getfromSina(key):

    key = '黑寡妇新海报'
    url = 'http://api.search.sina.com.cn/?c=news&q={}&stime=2018-08-25&etime=2019-08-27&sort=rel&highlight=1&num=10&ie=utf-8'.format(key)

    response = requests.get(url, headers=headers)
    text_json = json.loads(response.text.encode('utf-8'))
    content = text_json["result"]["list"]

    for json_reponse in content:

        url = json_reponse["url"]

        response = requests.get(url, headers=headers)
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
                        print(item.text)
                        exit()

        for item in lines:
            print(item)


    # # 创建一个进程池 Pool
    # pool = multiprocessing.Pool(multiprocessing.cpu_count())
    #
    # # 循环次数
    # for num in range(0, 30):
    #     pool.apply_async(geturl, (url, num, key)) # 多进程
    # pool.close()
    # # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数会等待所有子进程结束。
    # pool.join()



if __name__ == '__main__':

    titles = list()
    get_title()
    with open('../data/title.csv', 'r', encoding='utf-8') as csvFile:
        f_csv = csv.reader(csvFile)
        for row in f_csv:
            if row[1] != 'Title':
                titles.append(row[1])

    for key in titles:
        real_urls = getfromSina(key)
    # print(real_urls)










