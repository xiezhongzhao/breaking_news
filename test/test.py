#!/usr/bin/env python
# encoding: utf-8

# @Author: Xie Zhongzhao
# @Date  : 2019-09-02 10:12:00

from src.core.search_sina import GetSina

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


































