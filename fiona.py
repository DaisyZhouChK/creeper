# -*- coding: cp936 -*-
import urllib2
from bs4 import BeautifulSoup
import threading

#����mongodb���ݿ�
import pymongo
connection = pymongo.Connection("localhost",27017)
#���ݿ�����Ϊ forum_account
db = connection["forum_account"]
#�ۼ�����Ϊ Forum
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
#��ÿ������е�һƪ���µ�url������º�ĵ�һƪ���µ�url����ƥ��

global length_mod
global length_pas
#����ģ��
def tra_mod(nums):
    length_mod = len(nums)
    n = 0
    while n < length_mod:
        #�б��е�ÿ������ȡ����֮����������
        #ÿ��ģ�������
        url_mod = nums[n]["href"]
        #ÿ��ģ�������
        name_mod = nums[n].get_text()
        n = n + 1
        url_mod_list.append(url_mod)
    
#����ģ���ڵ�����
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
            #����һƪ���µ�url����url_pas_first_list��
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
            #�ڶ���relevant_tags�Ͱ��������ı����������ı�����
            attrsList = relevant_tags.attrs
            if len(author_temp) == 1:
                dic["author"] = author_temp[0]["usernick"]
            if "content_path" in attrsList:
                page4 = urllib2.urlopen(relevant_tags["content_path"])
                soup4 = BeautifulSoup(page4)
                dic["content"] = soup4.get_text()
            #����ر�ǩ���治����content_path��һ������ʱ
            else:
                content = relevant_tags.get_text()
                dic["content"] = content
            dic["title"] = soup3.title.get_text()
            dic["url"] = url_pas_list[n]
             #���������ݽ�������б�����б���Ƕ���ֵ䣬�ֵ��������content��author��title
               #�� url
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

#ȡ����ǿ����̳����ҳ
page = urllib2.urlopen("http://bbs1.people.com.cn/board/1.html")
soup = BeautifulSoup(page)
topics = soup.find_all("div","hotTopic")
#for topic in topics
topics = topics[0]
topics1 = topics.find_all("ul","navList clearfix")
topics2 = topics.find_all("ul","originalNav clearfix")
#�õ����в�ͬģ���<li><a>��ǩ
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

