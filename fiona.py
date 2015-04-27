# -*- coding: cp936 -*-
import urllib2
from bs4 import BeautifulSoup
import threading

#连接mongodb数据库
import pymongo
connection = pymongo.Connection("localhost",27017)
#数据库名称为 forum_account
db = connection["forum_account"]
#聚集名称为 Forum
#
forum = db["Forum"]


dic_reply = {}
lis = []
dic = {}
url_mod_list = []
url_pas_list = []
url_content_list = []
content_list = []
url_pas_first_list = []
#存每个版块中第一篇文章的url，与更新后的第一篇文章的url进行匹配

global length_mod
global length_pas
#遍历模块
def tra_mod(nums):
    length_mod = len(nums)
    n = 0
    while n < length_mod:
        #列表中的每个对象取出来之后汉字乱码了
        #每个模块的链接
        url_mod = nums[n]["href"]
        #每个模块的名字
        name_mod = nums[n].get_text()
        n = n + 1
        url_mod_list.append(url_mod)
    
#遍历模块内的文章
def tra_pas(y):
    m = 0
    while m < len(y):
        page2 = urllib2.urlopen(url_mod_list[m])
        soup2 = BeautifulSoup(page2)
        m = m + 1
        passages = soup2.find_all("div","replayWrap scrollFlag")
        #print len(passages)
        if len(passages) > 0:
            passages = passages[0]
            passages = passages.find_all("ul","replayList clearfix")
            passages = passages[0]
            relevant_tags = passages.find_all("a","treeReply")
            length_pas = len(relevant_tags)
            #print length_pas
            n = 0
            #将第一篇文章的url存在url_pas_first_list中
            url_pas = relevant_tags[n]["href"]
            url_pas_first_list.append(url_pas)
            while n < length_pas:
                url_pas = relevant_tags[n]["href"]
                #print url_pas
                url_pas_list.append(url_pas)
                n = n + 1
        #else:
            

def tra_content(z):
    n = 0
    #to store all the datas into a list
    while n < len(z):
        try:
            page3 = urllib2.urlopen(url_pas_list[n])
            n = n + 1
            soup3 = BeautifulSoup(page3)
            author_temp = soup3.find_all("div","articleInfo clearfix")
            author_temp = author_temp[0].find_all("img","portrait")
            contents = soup3.find_all("article")
            relevant_tags = contents[0].find_all("div","article scrollFlag")
            relevant_tags = relevant_tags[0]
            #第二个relevant_tags就包括正文文本或者正文文本链接
            attrsList = relevant_tags.attrs
            if len(author_temp) == 1:
                dic["author"] = author_temp[0]["usernick"]
            if "content_path" in attrsList:
                page4 = urllib2.urlopen(relevant_tags["content_path"])
                soup4 = BeautifulSoup(page4)
                dic["content"] = soup4.get_text()
            #当相关标签里面不存在content_path这一项属性时
            else:
                content = relevant_tags.get_text()
                dic["content"] = content
            dic["title"] = soup3.title.get_text()
            dic["url"] = url_pas_list[n]
             #将最后的数据结果存在列表里，在列表中嵌套字典，字典的属性有content，author，title
               #和 url
            reply_temp = soup3.find_all("li","treeReplyItem")
            reply_content = reply_temp[0].find_all("a","treeReply")
            reply_author_temp = reply_temp[0].find_all("a","userNick")
            a = 0
            lis_reply = []
            while a < len(reply_content):
                dic_reply = {}
                dic_reply["author"] = reply_author_temp[a].get_text()
                dic_reply["content"] = reply_content[a].get_text()
                a = a + 1
                lis_reply.append(dic_reply)
            dic["reply"] = lis_reply
            db.Forum.insert(dic)
            print "======================passage"+str(n)+"==========================="
        except:
            pass

def repetition():
    url_pas_new = []

    m = 0
    while m < len(url_mod_list):
        page2 = urllib2.urlopen(url_mod_list[m])
        soup2 = BeautifulSoup(page2)
        m = m + 1
        passages = soup2.find_all("div","replayWrap scrollFlag")
        #print len(passages)
        if len(passages) > 0:
            passages = passages[0]
            passages = passages.find_all("ul","replayList clearfix")
            passages = passages[0]
            relevant_tags = passages.find_all("a","treeReply")
            length_pas = len(relevant_tags)
            n = 0
            while n < length_pas:
                url_pas = relevant_tags[n]["href"]
                #print url_pas
                if url_pas is url_pas_first_list[n]:
                    break
                url_pas_new.append(url_pas)
                n = n + 1
        #else:

    tra_content(url_pas_new)

#取出“强国论坛”首页
page = urllib2.urlopen("http://bbs1.people.com.cn/board/1.html")
soup = BeautifulSoup(page)
topics = soup.find_all("div","hotTopic")
#for topic in topics
topics = topics[0]
topics1 = topics.find_all("ul","navList clearfix")
topics2 = topics.find_all("ul","originalNav clearfix")
#得到所有不同模块的<li><a>标签
topic1 = topics1[0]
topic2 = topics1[1]
topic3 = topics1[2]
topic4 = topics2[0]
topics1 = topic1.find_all("a")
topics2 = topic2.find_all("a")
topics3 = topic3.find_all("a")
topics4 = topic4.find_all("a")
tra_mod(topics1)
tra_mod(topics2)
tra_mod(topics3)
tra_mod(topics4)
tra_pas(url_mod_list)
tra_content(url_pas_list)
global t
t = threading.Timer(43200.0,repetition)
t.start()

