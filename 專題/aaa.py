import requests,os
from bs4 import BeautifulSoup
from flask import Flask
from flask import render_template

r = requests.get("https://udn.com/news/cate/2/6645") #將網頁資料GET下來
soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
    #sel = soup.select("div.story-list__text a")  #取HTML標中的 <div class="title"></div> 中的<a>標籤存入sel
titles = soup.find_all('a',{'data-story_list':'list_股市'})
column, row = 100, 100
b = [range(row) for _ in range(column)]
a = [range(row) for _ in range(column)]
c = [range(row) for _ in range(column)]
zzzz=0
for s in titles:
    a[zzzz]=s.text
    b[zzzz]="https://udn.com/"+s["href"]
    zzzz=zzzz+1
    if zzzz>=100:
        break;

r = requests.get("https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX20.html") #將網頁資料GET下來
soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
#sel = soup.select("a.Pos(a) W(100%) H(100%) T(0) Start(0) Z(0) div")  #取HTML標中的 <div class="title"></div> 中的<a>標籤存入sel
titles = soup.find_all("div", {"data-table":"td"})
#sel = soup.select("div.title h1")

#for s in titles:
    #print(s.text) 

ee= requests.get("https://tw.stock.yahoo.com/")
sel= BeautifulSoup(ee.text,"html.parser")
titles = sel.find_all("div", "Mx(20px) Mend(0)--wide")
az=1
for s in titles:
    c[az]=s.text
    print(c[az])
    az=az+1
    if az >=100:
        break;
     