# -*- coding: utf-8 -*-


from kssum.submodular import SubmodularSummarizer
import math
import json


cnsummarizer = SubmodularSummarizer('chinese')
ensummarizer = SubmodularSummarizer('english')

def get_summary(
        article,
        language='chinese',
        slimit=None,
        wlimit=None,
        ratio=None,
):
    global cnsummarizer
    global ensummarizer

    if language.startswith('ch'):
        if slimit:
            reslist = cnsummarizer(article, sents_limit=slimit)
        elif wlimit:
            reslist = cnsummarizer(article, words_limit=wlimit)
        else:
            words_limit = len(unicode(article)) * ratio
            words_limit = int(math.floor(words_limit))
            reslist = cnsummarizer(article, words_limit=words_limit)
    elif language.startswith('en'):
        if slimit:
            reslist = ensummarizer(article, sents_limit=slimit)
        elif wlimit:
            reslist = ensummarizer(article, words_limit=wlimit)
        else:
            words_limit = len(article.split()) * ratio
            words_limit = int(math.floor(words_limit))
            reslist = ensummarizer(article, words_limit=words_limit)

    if not reslist:
        return []

    diclist = []
    for res in reslist:
        tmpdict = {}
        tmpdict['sentence'] = res[0]
        tmpdict['index'] = res[1]
        diclist.append(tmpdict)
    return json.dumps({'result':diclist}, ensure_ascii=False)


if __name__ == "__main__":
    text = u'北京时间4月25日，今天休斯顿火箭主场以100-93战胜犹他爵士，以总比分4-1晋级。连续第2季淘汰爵士，这支火箭也终于为当年的姚麦组合报了一箭之仇。尽管后3场陷入苦战，但火箭今天没让煮熟的鸭子飞走，仍在主场获胜，进而以4-1淘汰爵士，进军西区次轮。而这也是火箭连续第2个赛季淘汰爵士。2017-18赛季，火箭在西区次轮也曾淘汰爵士，总比分同样是4-1。而这也是火箭连续第2个赛季淘汰爵士。'
    entext = 'Sri Lankan police are hunting a man in a distinctive red T-shirt who is suspected of being the Easter Sunday bombers’ handler, police sources have revealed. CCTV footage obtained by MailOnline shows the man apparently acting as a lookout for the terrorist who attacked St Sebastian’s Church, killing more than 100. Investigators are analysing the footage, hoping that it will help them root out the extensive Islamist cell that remains a threat on the island.'
    # reslist = summarizer(text, words_limit=100)
    # text = [res[0] for res in reslist]
    # print (''.join(text))
    reslist = get_summary(entext, language='english', wlimit=140)
    print(reslist)
    print(entext[0:156])
