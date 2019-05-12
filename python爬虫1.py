# -*- coding:UTF-8 -*-
import requests
from bs4 import BeautifulSoup
from time import sleep
import random
import os
import tkinter

def get_mes():
    global key_str
    key_str = entry1.get()
    print(u'检索内容:' + key_str)  # 获取文本框的内容
    win.destroy()

def gui():
    global entry1, win
    win = tkinter.Tk()
    win.title(u"燕大图书馆小助手")
    win.geometry("300x200")
    entry1 = tkinter.Entry(win, width=100, bg="gray", fg="black")
    entry1.pack()
    button = tkinter.Button(win, text=u"一键获取", command=get_mes)  # 收到消息执行这个函数
    button.pack()  # 加载到窗体，
    # entry1=tkinter.Entry(win,show="*",width=50,bg="red",fg="black")
    win.mainloop()

def getHtmlTree(url):
    response = requests.get(url, headers=headers, proxies=proxies)  # 申请得到的初始网页
    soup = BeautifulSoup(response.text, 'lxml')
    return soup

def get_ip_list(ip_url, headers):
    web_data = requests.get(ip_url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list

def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('https://' + ip)
    proxy_ip = random.choice(proxy_list)
    proxies = {'https': proxy_ip}
    return proxies

def delay():
    i = j = 1000
    while i > 0:
        if j % 1000 == 0:
            i = i - 1
        while j > 0:
            if i % 1000 == 0:
                j = j - 1
            while i < 1000:
                if j % 1000 == 0:
                    i = i + 1
                while j < 1000:
                    if i % 1000 == 0:
                        j = j + 1

def new_file():
    global filename
    file = 'D:/youshelf'
    filename=file+'/'+key_str+'.txt'
    if os.path.exists(file):
        os.chdir(file)
    else:
        os.mkdir(file)
        os.chdir(file)
    with open(filename, "w", encoding="UTF-8") as f:
        f.write('你的书架:\n')


if __name__ == '__main__':
    gui()
    # key_str='鲁迅全集'
    ip_url = 'http://www.xicidaili.com/nn/'
    start_url = 'http://202.206.242.99:8080/opac/openlink.php?strSearchType=title&match_flag=forward&historyCount=1&strText=' + key_str + '&doctype=ALL&displaypg=20&showmode=list&sort=CATA_DATE&orderby=desc&location=ALL'
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'close',
    }
    ip_list = get_ip_list(ip_url, headers=headers)
    proxies = get_random_ip(ip_list)
    print(proxies)
    new_file()
    # with open("D:/text.txt", "w", encoding="UTF-8") as f:
    #     f.write('你的书架:\n')
    start_html = requests.get(start_url, headers=headers, proxies=proxies)  # 申请得到的初始网页
    start_soup = BeautifulSoup(start_html.text, 'lxml')
    mark = start_soup.find_all('font')
    if mark[1].text == '0':
        print(u'抱歉，小助手努力了很久也没找到您检索的图书!')
        print(u' >_< !!!\n')
    try:
        max_page = start_soup.find('font', color='black').get_text()  # 最大页数
    except:
        max_page = 1
    for page in range(1, int(max_page)+1):
        url = start_url + '&page=' + str(page)
        html = requests.get(url, headers=headers, proxies=proxies)  # 申请得到的网页
        soup = BeautifulSoup(html.text, 'lxml')
        publications_list = soup.find_all('li', class_='book_list_info')
        for publications in publications_list[0:]:
            status_base_url = publications.find('a')['href']
            status_url = 'http://202.206.242.99:8080/opac/' + status_base_url
            name = publications.find('h3').find('a').get_text()
            author = publications.find('p').get_text()
            print(name)
            with open(filename, "a", encoding="UTF-8") as f:
                f.write(name + '\n')
            status_html = requests.get(status_url, headers=headers, proxies=proxies)
            status_soup = BeautifulSoup(status_html.text, 'lxml')
            all_local = status_soup.find_all('tr', class_="whitetext")
            for local in all_local:
                area_list = local.find_all('td', width='25%')  # 馆藏地
                if len(area_list):
                    print(u'馆藏地:' + area_list[0]['title'] + '  ' + u'书刊状态:' + area_list[1].text)
                    with open(filename, "a", encoding="UTF-8") as f:
                        f.write(u'馆藏地:' + area_list[0]['title'] + '  ' + u'书刊状态:' + area_list[1].text + '\n')
                else:
                    print(u'此书刊没有复本,可能正在订购中或者处理中!!!')
                    with open(filename, "a", encoding="UTF-8") as f:
                        f.write(u'此书刊没有复本,可能正在订购中或者处理中!!!')
                print('\n')
            with open(filename, "a", encoding="UTF-8") as f:
                f.write('<==============================================>\n')

