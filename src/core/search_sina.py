#!/usr/bin/env python
# encoding: utf-8

# @Author: Xie Zhongzhao
# @Date  : 2019-09-02 10:12:00

import requests
import warnings
import bs4
import json
import jieba
import time
import csv

from bs4 import BeautifulSoup
from src.core.kssum.run_submodular import get_summary

warnings.filterwarnings('ignore')

class GetSina(object):

    def __init__(self):
        # 定义头文件，伪装成浏览器
        self.headers = {"User-Agent":
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
        self.title_dir = '../data/title.csv'
        self.etime = time.strftime("%Y-%m-%d", time.localtime())

    def get_title(self):
        '''
        从百度热点中获得热点标题
        :return: 返回从百度爬取的热点标题
        '''
        titles = list()
        # html = get_title()
        # get_pages(html)
        with open(self.title_dir, 'r', encoding='utf-8') as csvFile:
            f_csv = csv.reader(csvFile)
            for row in f_csv:
                if row[1] != 'Title':
                    titles.append(row[1])

        return titles

    def get_url_sina(self, title):
        '''
        根据热点标题key, 在新浪上获得热点文章的url
        :param key: 热点标题
        :return: 与热点标题有关的热点文章url
        '''
        stime = '2000-01-01'
        etime = self.etime

        url = 'http://api.search.sina.com.cn/?c=news&q={}' \
              '&stime={}&etime={}&sort=rel&highlight=1&num=10&ie=utf-8'.format(title, stime, etime)

        try:
            response = requests.get(url, headers=self.headers)
            text_json = json.loads(response.text.encode('utf-8'))
            urls = text_json["result"]["list"]
        except:
            return False

        return urls

    def get_text_sina(self, key, urls_list, num_parts):
        '''
        爬取对应的热点文章
        :param key: 热点标题
        :param urls_list: 热点文章的urls
        :param num_parts: 将文章分为n个段落
        :return: 返回有n个段落的文章
        '''
        if not urls_list:
            return False

        articles_url = list()
        articles_list = list()
        big_texts = list()

        hot_key = list(jieba.cut(key, cut_all=False))

        #获取热点文章的URL, 并且解析热点文章
        for json_reponse in urls_list:

            url = json_reponse["url"]
            response = requests.get(url, headers=self.headers)
            text = response.content.decode("utf-8")
            soup = BeautifulSoup(text, "html.parser") # 解析热点文章
            title = soup.title
            try:
                title_list = list(jieba.cut(title.text, cut_all=False))  # 热点文章分词
            except:
                continue

            if list(set(hot_key).union(set(title_list))): # 过滤与热点标题无关的文章

                result = str(soup.find("div", id='artibody'))
                subsoup = BeautifulSoup(result, "html.parser")

                essay = []
                for item in subsoup.find_all('p'):
                    if isinstance(item, bs4.element.Tag):
                        if item.name == "p":
                            if item.text:
                                essay.append(item.text)

                articles_url.append(url)
                articles_list.append(essay)

        #将文章分为四个部分, 分别对四个部分进行信息提取
        # print(articles_url)

        article_length = [len(article) for article in articles_list]
        index = article_length.index(max(article_length))

        num_sentences = len(articles_list[0])
        step = num_sentences // num_parts

        for i in range(0, num_parts):
            big_texts.append(''.join([sentence for sentence in articles_list[index][step*i:step*(i+1)]]))

        return big_texts

    def generate_article(self, texts):
        '''
        将n个段落运用次模函数逐段抽取, 拼接
        :param texts: 分为n个段落的文章
        :return: 返回抽取式生成的文章
        '''
        if len(texts) == 0:
            return False

        article = list()
        for text in texts: # 次模函数进行句子抽取
            try:
                extract_text = get_summary(text, language='chinese', wlimit=150, ratio=None)
            except:
                continue

            if extract_text: # 次模函数返回是否为空
                try:
                    extract_text = json.loads(extract_text, encoding=False)
                    extract_sentences = extract_text['result']
                except:
                    return False

                tmp = list()
                for sentence in extract_sentences:
                    tmp.append(sentence['sentence'])

                article.append("".join(tmp))

        return article

if __name__ == '__main__':

    # 调用新浪的类
    sina = GetSina()
    titles = set(sina.get_title()) # 获取热点标题
    print(titles)

    num_essay = 0
    for title in titles:

        print("title: ", title)

        urls = sina.get_url_sina(title) # 获取热点文章的url
        texts = sina.get_text_sina(title, urls, 4) # 获得热点主题对应的文章

        if texts:

            article = sina.generate_article(texts) # 抽取式生成文章

            if article:
                num_essay += 1
                for para in article:
                    print(para, '\n')
            else:
                print("no related articles")
        else:
            print("no related articles")
        print("*" * 100, '\n')

    print("num_essay: ", num_essay)
    print("Recall: %.4f"%(num_essay/len(titles)))










