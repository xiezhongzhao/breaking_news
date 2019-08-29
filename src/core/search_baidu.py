import requests
from bs4 import BeautifulSoup

def baidunew_search(key):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}

    all_context = []
    url = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={}".format(key)
    response = requests.get(url,headers=headers)
    content = response.content.decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    for item in soup.find_all(attrs={"class": "result"}):
        cauthor = item.div.p.text
        title = item.a.text.strip()
        origin = cauthor[:cauthor.index("\t")].strip()
        time = cauthor[cauthor.index("\t"):].strip()
        url = item.h3.a["href"]
        all_context.append((title,origin,time,url))

    pagesoup = BeautifulSoup(content, "html.parser")
    pages=pagesoup.find("p",id ="page")
    for i,item in enumerate(pages.find_all("a")):
        if i >9:
            break
        para = item["href"]
        pageurl= "https://www.baidu.com"+item["href"]
        response = requests.get(pageurl, headers=headers)
        content = response.content.decode("utf-8")
        soup = BeautifulSoup(content, "html.parser")
        for item in soup.find_all(attrs={"class":"result"}):
            cauthor = item.div.p.text
            title = item.a.text.strip()
            origin = cauthor[:cauthor.index("\t")].strip()
            time = cauthor[cauthor.index("\t"):].strip()
            url = item.h3.a["href"]
            all_context.append((title,origin,time,url))
    return all_context

for item in baidunew_search("台风白鹿逼近闽粤"):
    print(item)
