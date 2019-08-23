import time
import urllib3
import logging
import re
import requests

from scrapy.http.response import html
from urllib.parse import quote
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

chars_punc = ",;.!?:'\"、，；。！？：‘“"
chars_digit = "1234567890"
reg_cn_text = re.compile("[^\u4E00-\u9FFF|\s{}{}]+".format(chars_punc, chars_digit))
reg_ch_chs = re.compile("[^\u4E00-\u9FFF]+")

def get_docs(keyword, fn_callback, url_num=20):

    def __links(_keyword):
        timer = time.time()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/72.0.3626.121 Safari/537.36',
            'Host': 'www.baidu.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'Connection': 'keep-alive',
        }
        url_format = "https://www.baidu.com/s?wd={}&rn={}"
        url = url_format.format(quote(_keyword), url_num)
        req = requests.get(url=url, verify=False, headers=headers)

        if not req or not req.content:
            logger.info("NoContentError:%s", url)
            return

        response = html.HtmlResponse(encoding='utf-8', url=url, headers=headers, body=req.content)
        links = response.xpath('//div[@id="content_left"]/div[@class="result c-container "]/h3/a/@href').extract()

        logger.info("time:%s", time.time() - timer)
        return links

    keyword = keyword.strip() if keyword else None
    if not keyword: return
    links = __links(keyword)
    links_len = len(links)
    links_num = min(url_num, links_len)
    for i in range(links_num):
        get_doc(links[i], fn_callback)

def get_doc(url, fn_callback):

    target_url = url

    def __domain(url:str):
        start = url.index("://")
        if start:
            temp_str = url[start + 4:]
            end = temp_str.index("/")
            return url[0:(end + start + 4)] if end else url
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/72.0.3626.121 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'Connection': 'keep-alive',
        }
        req = requests.get(url, headers=headers, verify=False, timeout=10)
        target_url = req.url
        try:
            raw_html = req.content.decode("utf-8")
        except Exception as e:
            raw_html = req.content.decode('gbk')
        text = clean_text(raw_html, target_url)
        if text and len(text) > 300:
            doc = {"domain": __domain(target_url), "url": target_url, "text": text, "raw_html": raw_html}
            fn_callback(doc)
    except Exception as e:
        logger.warning(str(e) + ": " + target_url)

def clean_text(raw_html, url):
    def __handle_line(line:str):
        result = ""
        line = line.replace("|","")
        line = line.strip()
        prev_is_punc = True
        for ch in line:
            if not ch.strip(): continue
            if ch not in chars_punc:
                result = result + ch
                prev_is_punc = False
            elif not prev_is_punc:
                result = result + ch
                prev_is_punc = True
        line_cn = reg_ch_chs.sub("",result)
        result_len = len(result)
        rate_cn = len(line_cn) / result_len if result_len > 0 else 0
        return result if rate_cn >= 0.7 else ""

    soup = BeautifulSoup(raw_html, features="lxml")
    raw_text = reg_cn_text.sub("", soup.get_text())
    lines = raw_text.split("\n")
    text = ""
    prev_len = -1
    for line in lines:
        line = __handle_line(line)
        line_len = len(line)
        if line_len >= 45:
            text = text + line + "\n"
            prev_len = line_len
        elif prev_len >= 45 and line_len >= 15:
            text = text + line + "\n"
            prev_len = line_len
        else:
            prev_len = 0
    return text

if __name__ == "__main__":
    fn_print = lambda x: print(x)
    get_docs("郎朗为娇妻庆生",fn_print)