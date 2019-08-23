import requests
from bs4 import BeautifulSoup
import csv

def get_title():
    #百度热点排行榜单链接
    url = 'http://top.baidu.com/buzz?b=1&fr=20811' #实时热点
    # url = 'http://top.baidu.com/buzz?b=11&c=513&fr=topbuzz_b1_c513' #体育热点

    headers = {'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, image/webp, image/apng, */*;q=0.8, application/signed-exchange; v = b3',
               'Accept-Encoding' : 'gzip, deflate',
               'Accept-Language': 'en-US, en; q=0.9',
               'Connection': 'keep-alive',
               'Cookie': 'BAIDUID=317F0C1E645392463E0FF767B8F5BA86:FG=1; '
                         'pgv_pvi=1064096768; pgv_si=s6449092608; '
                         'BIDUPSID=317F0C1E645392463E0FF767B8F5BA86; '
                         'PSTM=1566468353; delPer=0; PSINO=7; '
                         'H_PS_PSSID=1431_21111_29523_29518_29099_29568_29220; '
                         'BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; Hm_lvt_79a0e9c520104773e13ccd072bc956aa=1566526869;'
                         ' bdshare_firstime=1566526869708; '
                         'BDRCVFR[z91LIEeorFR]=mk3SLVN4HKm; '
                         'Hm_lpvt_79a0e9c520104773e13ccd072bc956aa=1566528144',
               'Host': 'top.baidu.com',
               'User-Agent': 'Mozilla/5.0'}

    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    return r.text

def get_pages(html):

   with open("../data/title.csv", 'w', encoding='utf-8') as csv_file:

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
               # print('排名：{}，标题：{}，热度：{}'.format(topic_rank,topic_name,topic_times))
               title_list = list()
               title_list.append(topic_rank)
               title_list.append(topic_name)
               writer.writerow(title_list)

# test
if __name__ == '__main__':

    titles = list()
    html = get_title()
    get_pages(html)

    with open('../data/title.csv', 'r', encoding='utf-8') as csvFile:
        f_csv = csv.reader(csvFile)
        for row in f_csv:
            if row[1] != 'Title':
                titles.append(row[1])
    print(titles)



































