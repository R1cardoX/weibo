import signal
import requests
import random
import time
from bs4 import BeautifulSoup
import urllib.error
import urllib.parse
import urllib.request
import re
import rsa
import http.cookiejar
import base64
import urllib
import json
import pandas as pd
import numpy as np
import binascii
import aiohttp
import asyncio
import multiprocessing as mp
import threading
import sys
import os
class Scrapy:
    t0 = time.time()
    count = 0
    connect_count = 0
    login_url = "https://weibo.com"
    cookies_pool = []
    def __init__(self,time = 10):
        self.time = time
        self.user_pool = self.init_users()
        self.headers_pool = self.init_headers()

    def init_headers(self):
        file = open('./res/headers','r')
        headers_group = []
        for headers in file.readlines():
            headers = {"User-Agent":headers.strip('\n')}
            headers_group.append(headers)
        return headers_group

    def init_cookies(self,times = 3):
        cookies_pool = []
        i = 0
        for _ in range(times):
            for user in self.user_pool:
                cookies = self.login(user)
                print('Get cookies No.',i+1,"with user:",user[0])
                cookies_pool.append(cookies)
                i += 1
        print('\n................................cookies_pool len:',len(cookies_pool))
        self.t0 = time.time()
        return cookies_pool
    
    def init_users(self):
        file = open('./res/userform','r')#格式 用户名:密码
        users_group = []
        for users in file.readlines():
            users = (users.strip('\n').split(':')[0],users.strip('\n').split(':')[1])
            users_group.append(users)
        return users_group

    def get_encrypted_name(self,user):
        username_urllike = urllib.request.quote(user[0])
        username_encrypted = base64.b64encode(bytes(username_urllike,encoding = 'utf-8'))
        return username_encrypted.decode('utf-8')

    def get_prelogin_args(self,user):
        '''
        模拟预登陆 获取服务器返回的 nonce ，servertime，pub_key 等信息
        '''
        json_pattern = re.compile('\((.*)\)')
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=' + self.get_encrypted_name(user) + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)'
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            raw_data = response.read().decode('utf-8')
            json_data = json_pattern.search(raw_data).group(1)
            data = json.loads(json_data)
            return data
        except urllib.error as e:
            print("%d"%e.code)
            return None

    def get_encrypted_pw(self,data,user):
        rsa_e = 65537
        pw_string = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' +str(user[1])
        key = rsa.PublicKey(int(data['pubkey'],16),rsa_e)
        pw_encypted = rsa.encrypt(pw_string.encode('utf-8'),key)
        self.password = ''
        passwd = binascii.b2a_hex(pw_encypted)
        return passwd
        
    def build_post_data(self,raw,user):
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "useticket": "1",
            "pagerefer": "https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F",
            "vsnf": "1",
            "su": self.get_encrypted_name(user),
            "service": "miniblog",
            "servertime": raw['servertime'],
            "nonce": raw['nonce'],
            "pwencode": "rsa2",
            "rsakv": raw['rsakv'],
            "sp": self.get_encrypted_pw(raw,user),
            "sr": "1440*900",
            "encoding": "UTF-8",
            "prelt": "329",
            "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        return post_data

    def login(self,user):
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        p = re.compile('location\.replace\(\"(.*?)\"\)')
        p1 = re.compile('location\.replace\(\'(.*?)\'\)')
        p2 = re.compile(r'"uniqueid":"(\d*?)"')
        headers = random.sample(self.headers_pool,1)[0]
        data = self.get_prelogin_args(user)
        post_data = self.build_post_data(data,user)
        try:
            request = requests.post(url = url,data = post_data,headers = headers)
            login_url = p.search(request.text).group(1)
            time.sleep(0.5)
        except:
            print("login errer")
            print("..............................Error html:\n",request)
            return None
        self.login_url = login_url
        return request.cookies

    async def connect_url(self,url):
        if url is "":
            return None
        if self.count % 100 is 0 and self.count is not 0:
            print(self.count,".\tConnect url :",url,"\tuse time:",time.time()-self.t0)
        if self.count % 250 is 0:
            print("Get Cookies ...")
            self.cookies_pool = []
            self.cookies_pool = self.init_cookies(3)
        self.count += 1
        cookies = random.sample(self.cookies_pool,1)[0]
        headers = random.sample(self.headers_pool,1)[0]
        try:
            async with aiohttp.ClientSession(cookies = cookies) as session:
                async with session.get(url,headers = headers) as r:
                    html =await r.text()
                    await asyncio.sleep(self.time)
                    return html,1
        except:
            return url,0


def analyse_user_data(html):
    if html is None:
        return ""
    html1 = re.sub(re.compile(r'\\/'),"/",html)
    html2 = re.sub(re.compile(r'\\"'),"\"",html1)
    html3 = re.sub(re.compile(r'\\t'),"\t",html2)
    html4 = re.sub(re.compile(r'\\n'),"\n",html3)
    html5 = re.sub(re.compile(r'\\r'),"\r",html4)
    p = re.compile('href="(/\d+/follow\?rightmod=\d&wvr=\d)"')
    p1 = re.compile(r'<span\s*class="item_ico\s*W_fl">\s*<em\s*class="W_ficon\s*ficon_cd_place\s*S_ficon">[^<>]*</em>[^<>]*</span>[^<>]*<span\s*class="item_text\s+W_fl">\s*([^<>\s]+)\s*[^<>\s]*\s*</span>') 
    p2 = re.compile(r'<title>([^<>]+)</title>')
    p3 = re.compile(r'href="//weibo.com(/p/\d+/follow\?from=page_\d+&wvr=6&mod=headfollow#place)"')
    p4 = re.compile(r'href="(/\d+/fans\?\w+=\d+&\w+=\d+)"')
    p5 = re.compile(r'href="//weibo.com(/p/\d+/follow\?relate=fans&from=\d+&wvr=\d+&mod=headfans&current=fans#place)"')
    p6 = re.compile(r'简介：([^<>]+)')
    p7 = re.compile(r'href="(/\d+/profile\?rightmod=\d+&wvr=\d+&mod=personinfo)"')
    try:
        title = p2.search(html5).group(1).split("的微博")[0]
    except:
        #print("Search title error ...")
        title = ""
    try:
        match = p3.search(html5)
        if match is None:
            match = p.search(html5)
        att_url = "https://weibo.com" + match.group(1)
    except:
        #print("Search att url error\t\t\t\t\t\tError Title:",title)
        att_url = ""
    try:
        match = p5.search(html5)
        if match is None:
            match = p4.search(html5)
        fans_url = "https://weibo.com" + match.group(1)
    except:
        #print("Search fans url error\t\t\t\t\t\tError Title:",title)
        fans_url = ""
    try:
        location = p1.search(html5).group(1)
    except:
        #print("Search location error ...but get the url:",url,"\tError Title:",title)
        location = ""
    try:
        r_autograph = p6.search(html5).group(1)
        autograph = re.sub(re.compile(r'\s+')," ",r_autograph)
    except:
        #print("Search autograph error ...but get the url:",url,"\tError Title:",title)
        autograph = ""
    print("\nFrom title:",title,"\n\tGet att url:",att_url,"\n\tGet fans url:",fans_url,"\n\tLocation:",location,"\tAutograph:",autograph)
    return title,att_url,fans_url,location,autograph

def analyse_some_att(html):
    if html is None:
        return ""
    html1 = re.sub(re.compile(r'\\/'),"/",html)
    html2 = re.sub(re.compile(r'\\"'),"\"",html1)
    html3 = re.sub(re.compile(r'\\t'),"\t",html2)
    html4 = re.sub(re.compile(r'\\n'),"\n",html3)
    html5 = re.sub(re.compile(r'\\r'),"\r",html4)
    p = re.compile(r'action-data=\\"uid=(\d{1,15})&nick=(.+?)\\">')
    p2 = re.compile(r'<title>([^<>]+)</title>')
    try:
        title = p2.search(html5).group(1).split("的微博")[0]
    except:
        title = ""
    try:
        att = p.findall(html)
        url_list = []
        for _id in att:
            url = 'https://weibo.com/u/' + _id[0]# + '?from=myfollow_all'
            url_list.append(url)
            print("Get the user url:",url,"\t\tfrom ",title)
    except:
        return ""
    return set(url_list)


async def main(loop):
    pool = mp.Pool(4)
    url = "https://weibo.com/u/3195299207?from=myfollow_all"
    base_url = 'https://weibo.com/'
    seen = set()
    unseen = set([base_url])
    att_urls = set()
    lost_url = set()
    user = Scrapy()
    locations = pd.Series([0],index = ['北京'])
    file_userdata = open('./res/userdata','w')
    file_userdata.write("")
    while len(unseen) != 0 or len(att_urls) <= 10000 or user.count <= 10000:
        print('\nGet  attation url ing ...')
        tasks = [loop.create_task(user.connect_url(url)) for url in unseen]
        finished,unfinished = await asyncio.wait(tasks)
        datas = [f.result() for f in finished]
        htmls = []
        lost_url.clear()
        for data,flag in datas:
            if flag is 1:
                htmls.append(data)
            else:
                lost_url.add(data)
        att_urls.update(lost_url)
        print("\nSuccess get url:",len(htmls),"\tGet url error:",len(lost_url))


        print('\nAnalyse attation html ing ...')
        parse_jobs = [pool.apply_async(analyse_user_data,args=(html,)) for html in htmls]
        user_datas = [j.get() for j in parse_jobs]
        file_userdata = open('./res/userdata','a')
        for title,att_url,fans_url,location,autograph in user_datas:
            if att_url is "":
                continue
            elif att_url in att_urls:
                continue
            user_data = "title:" + title + "att_url:" + att_url + "fans_url:" + fans_url + "location:" + location + "autograph:" + autograph + "\n"
            file_userdata.writelines(user_data)
            if location is not "":
                if location in locations:
                    locations[location] += 1
                else:
                    locations[location] = 1
            att_urls.add(att_url)
            if fans_url is not "":
                att_urls.add(fans_url)
        print("\nLocations:\n",locations)
        locations.to_csv('./res/location.csv')

        print('\nGet some attation ing ...')
        tasks = [loop.create_task(user.connect_url(url)) for url in att_urls]
        finished,unfinished = await asyncio.wait(tasks)
        datas = [f.result() for f in finished]
        htmls = []
        lost_url.clear()
        for data,flag in datas:
            if flag is 1:
                htmls.append(data)
            else:
                lost_url.add(data)
        
        print('\nAnalyse some attation ing ...')
        parse_jobss = [pool.apply_async(analyse_some_att,args=(html,)) for html in htmls]
        url_lists = [j.get() for j in parse_jobss]

        print('\nUpdata seen ing ...')
        seen.update(unseen)
        unseen.clear()
        unseen.update(lost_url)
        for url_list in url_lists:
            unseen.update(url_list - seen)

        print('Use time:',time.time()-user.t0,'get user number:',len(seen)+len(unseen),'\n\t\t\tWait for connect user\'s url num:',len(unseen),'already connect user\'s url num:',len(seen))


def user_exit():
    while True:
        read = str(sys.stdin.readline())
        if 'exit' in read or 'quit' in read:
            print("将要退出程序",os.getpid())
            break
        read = ""
    os.kill(os.getpid(),signal.SIGINT)

if __name__ == "__main__":
    print("即将开始程序，这个操作会清空location.csv与userdata,如意需要请及时备份,输入任意键开始")
    if sys.stdin.readline() is not None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop))
        loop.close()
    else:
        print("已经退出")
    
    
