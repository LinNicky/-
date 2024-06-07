from cgi import test
from distutils.log import debug
from email import message
from http import server
import requests,os,sqlite3,re,time ,random,numpy,json
from bs4 import BeautifulSoup
from flask import Flask,send_file,make_response
from flask import  request, redirect, url_for,render_template
from flask import *
from werkzeug.utils import secure_filename
from flask_login import LoginManager
import mysql.connector,flask_excel
import pandas as pd
from datetime import datetime, date
from flask import send_from_directory
import requests as r
from lxml import etree
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
from fake_useragent import UserAgent
import plotly as py
import plotly.graph_objects as go
import numpy as np


connection = mysql.connector.connect(host = "localhost",
                                            port = "3306",
                                            user = "root",
                                            password = "a25201607",
                                            database = "account",
                                            charset = "utf8")



connection2 = mysql.connector.connect(host = "localhost",
                                            port = "3306",
                                            user = "root",
                                            password = "a25201607",
                                            database = "stocktest",
                                            charset = "utf8")

connection3 = mysql.connector.connect(host = "localhost",
                                            port = "3306",
                                            user = "root",
                                            password = "a25201607",
                                            database = "stocknumber",
                                            charset = "utf8")


app = Flask(__name__)
app.config['SECRET_KEY']= os.urandom(24)



if __name__ == '__main__':
    app.debug = True
    app.run()
global d ,df
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
ee= requests.get("https://tw.stock.yahoo.com/")
sel= BeautifulSoup(ee.text,"html.parser")
titles = sel.find_all("div", "Lh(20px) Fw(600) Fz(16px) Ell")
az=1
for s in titles:
    c[az]=s.text
    az=az+1
    if az >=100:
        break;

@app.route('/')
def index():
        
    return render_template('index1.html', aa=a ,bb=b,cc=c)

@app.route("/loginForm")
def loginForm():
    if 'username' in session:
        return redirect(url_for('index1.html'))
    else:
        return render_template('login.html',error='')

@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method =="POST":
        username = request.form['username']
        password = request.form['password']
        if is_valid(username,password):
            session['username'] = username
            session['password']=password
            return redirect(url_for('ww'))
        else:
            error = '帳號或密碼錯誤'
            return render_template('login.html',error = error)
    return render_template("login.html")
def is_valid(username,password):
    cursors = connection.cursor()
    cursors.execute('select username,password from love')
    data = cursors.fetchall()
    for row in data:
        if row[0]==username and row[1]==password:
            print(row[1])
            connection.close()
            return True
    return False

@app.route("/index2")
def ww():
    username=session.get('username')
    return render_template('index2.html',username=username,aa=a,bb=b,cc=c)

@app.route("/registration",methods = ["GET","POST"])
def registration():
    cursors = connection.cursor()
    msg = ""
    if request.method == "POST":
        pattern = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,20}$"
        password = request.form["password"]
        result = re.findall(pattern, password)
        if (result):
                try:
                    info = {
                        "username":request.form["username"],
                        "password":request.form["password"],
                        "email":request.form["email"]
                        }

                    cursors.execute("insert into love(username,password,email) values (%s,%s,%s)",(
                        info["username"],
                        info["password"],
                        info["email"],
                        
                        )) 
                            
                    connection.commit()
                    connection.close()
                    msg = "reg_success"

                    return redirect(url_for("index"))

                except Exception as e:
                    print(e)
                    connection.rollback()
                    msg = "帳號已存在"
        else:
            msg="密碼需有數字及英文大小寫各一"
    return render_template("registration.html",msg = msg)

@app.route("/accounts")
def accounts():
    username=session.get('username')
    password=session.get('password')
    email=session.get('email')
    return render_template('accounts.html',username=username,password=password,email=email)


@app.route("/products")
def products():
    username=session.get('username')
    password=session.get('password')
    email=session.get('email')
    return render_template('products.html',username=username,password=password,email=email)

@app.route("/search",methods=['POST', 'GET'])
def search():
    cur = connection2.cursor()
    username=session.get('username')
    password=session.get('password')
    if request.method == "POST":
        value=request.form['number']
        day=request.form['day1']
        day2=request.form['day2']
        df = pd.DataFrame()
        time=day[0]+day[1]+day[2]+day[3]+day[5]+day[6]+day[8]+day[9]
        time2=day2[0]+day2[1]+day2[2]+day2[3]+day2[5]+day2[6]+day2[8]+day2[9]
        print(value,time,time2)
        try:
            commend = "SELECT * FROM %s_10年 WHERE 日期 BETWEEN %s AND %s"%(value,time,time2)
            cur.execute(commend)
            result = cur.fetchall()
            #print(result)#股票資料
            print(result)
        except Exception as e:
            message="資料不存在"
            return render_template('search.html',message=message)
        df = df.append(result,ignore_index = True)
        for col in [0,1,2,3,4,5,6,8]:
            for row in range(df.shape[0]):
                if col!=0:
                    df.iloc[row,col] = float(df.iloc[row,col].replace(',',''))
        df.columns = ['日期','成交股數','成交金額','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
        print(df)
        df.to_csv("stock_info.csv",index=False,encoding="utf_8_sig")
        #test=request(send_file("1101.csv"))
        #print(result2[:,1])#公司名稱


        df.insert(9,"aaa",'')   #9
        df['成交量顏色'] = ''    #10
        df.insert(11,"RSV",'')   #11
        
    #.......................................................交易良顏色判斷........................................................
        for row in range(df.shape[0]):
            if row!=0:
                if (df.iloc[row,6]>df.iloc[row-1,6]):
                    df.iloc[row,10] = 'red'
                elif(df.iloc[row,6]==df.iloc[row-1,6]):
                    df.iloc[row,10] = 'gray'
                elif(df.iloc[row,6]<=df.iloc[row-1,6]):
                    df.iloc[row,10] = 'green'
            else:
                df.iloc[row,10] = 'red'
    #....................................................算RSV.....................................................
        for row in range(df.shape[0]):                  
            if row >= 8:
                min_day = float(df.iloc[row,5])
                max_day = float(df.iloc[row,4])
                for num in range(row-8,row+1):
                    if (float(df.iloc[num,5])<=min_day):
                        min_day = float(df.iloc[num,5])
                    if (float(df.iloc[num,4])>=max_day):
                        max_day = float(df.iloc[num,4])
                df.iloc[row,11] = ((float(df.iloc[row,6])-min_day)/(max_day-min_day))*100
                df.iloc[row,11] = round(float(df.iloc[row,11]),2)

    #.....................................................算 K  D........................................................

        df['K'] = ''      #[row,12]
        df['D'] = ''       #[row,13]
        for row in range(df.shape[0]):          
            if row == 8:
                df.iloc[row,12] = (50*2/3) + (df.iloc[row,11]/3)
                df.iloc[row,13] = (50*2/3) + (df.iloc[row,12]/3)
            elif row>8:
                df.iloc[row,12] = round(((df.iloc[row-1,12]*2/3) + (df.iloc[row,11]/3)),2)
                df.iloc[row,13] = round(((df.iloc[row-1,13]*2/3) + (df.iloc[row,12]/3)),2)

    #..................................................均線..........................................................

        df['MA5'] = df['收盤價'].rolling(5).mean()    #  均線[row,14]
        df['MA20'] = df['收盤價'].rolling(20).mean()   #均線[row,15] 
        df['MA60'] = df['收盤價'].rolling(60).mean()    #均線[row,16]

    #..............................................計算MACD.........................................................
        df["EMA12"] = df["收盤價"].ewm(span = 12 , adjust = False).mean()    #17
        df["EMA26"] = df["收盤價"].ewm(span = 26 , adjust = False).mean()    #18 
        df["DIF"] = df["EMA12"] - df["EMA26"]                                #19
        df["MACD"] = df["DIF"].ewm(span = 9, adjust = False).mean()          #20
        df["OSC"] = df["DIF"] - df["MACD"]                                   #21
        
        #.............................................計算OSC(柱狀圖)..........................................................
        #df['OSC'] = df['DIF'] - df['MACD']                     
        
        df.insert(22,"OSC_color",'')
        for i in range(df["OSC"].shape[0]):
            if df.iloc[i,21]>=0:
                df.iloc[i,22] = 'red'
            else:
                df.iloc[i,22]  ='green'
        
    #..............................................................................................................
        fig2 = make_subplots(
            rows = 4,
            cols = 1,
            shared_xaxes = True,  #共享X軸
            vertical_spacing = 0.05,    #子圖間隔
            row_width = [1.3,1.3,1.3,3.8])

        #...................................................K線圖....................................................

        fig2.add_trace(go.Candlestick(                                       
                                    x = df['日期'],
                                    open = df['開盤價'],
                                    high = df['最高價'],
                                    low = df['最低價'],
                                    close = df['收盤價'],
                                    increasing_line_color = 'red',
                                    decreasing_line_color = 'green',
                                    name ='K線圖'),
                    row = 1,
                    col = 1)
        #.....................................................均線...........................................................
        fig2.add_trace(go.Scatter(
                                x = df['日期'],
                                y = df['MA5'],
                                line = dict(color = 'blue' , width = 1),
                                name = 'MA5',
                                mode = 'lines'),
                    row = 1,
                    col = 1)
        
        fig2.add_trace(go.Scatter(
                                x = df['日期'],
                                y = df['MA20'],
                                line = dict(color = 'orange' , width = 1),
                                name = 'MA20',
                                mode = 'lines'),
                    row = 1,
                    col = 1)

        fig2.add_trace(go.Scatter(
                                x = df['日期'],
                                y = df['MA60'],
                                line = dict(color = 'green' , width = 1),
                                name = 'MA60',
                                mode = 'lines'),
                    row = 1,
                    col = 1)            
    #..............................................................交易量............................................................

        fig2.add_trace(go.Bar(                               
                            x = df['日期'],
                            y = df['成交金額'],
                            showlegend = False,
                            name = '成交股數',
                            marker_color = df["成交量顏色"]),
                    row = 2,
                    col = 1)
    #....................................................RSV.........................................................
        fig2.add_trace(go.Scatter(                               
                            x = df['日期'],
                            y = df['RSV'],
                            line = dict(color = 'gray' , width = 1),
                            name = 'RSV'),
                row = 3,
                col = 1)
        fig2.add_trace(go.Scatter(
                            x = df['日期'],
                            y = df['K'],
                            line = dict(color = 'red', width = 1),
                            name = 'K9',
                            mode = 'lines'),
                row = 3,
                col = 1)
        fig2.add_trace(go.Scatter(
                            x = df['日期'],
                            y = df['D'],
                            line = dict(color = 'green', width = 1),
                            name = 'D9',
                            mode = 'lines'),
                row = 3,
                col = 1)

    #.............................................MACD(平滑異同移動平均線指標)...................................

        fig2.add_trace(go.Scatter(
                            x = df['日期'],
                            y = round(df['MACD'],2),
                            line = dict(color = 'blue', width = 1),
                            name = 'MACD',
                            mode = 'lines',),
                row = 4,
                col = 1)
        fig2.add_trace(go.Scatter(
                            x = df['日期'],
                            y = round(df['DIF'],2),
                            line = dict(color = 'orange', width = 1),
                            name = 'DIF',
                            mode = 'lines',),
                row = 4,
                col = 1)
        fig2.add_trace(go.Bar(
                            x = df['日期'],
                            y = round(df['OSC'],2),
                            name = 'OSC',
                            marker_color = df["OSC_color"]),
                row = 4,
                col = 1) 
        fig2.update_xaxes(rangebreaks = [{'pattern' : 'day of week', 'bounds' : [6,1]}])
        fig2.update_xaxes(title = '日期' , row = 4 , col = 1)
        fig2.update_yaxes(title = '股價' , row = 1 , col = 1)
        fig2.update_yaxes(title = '成交量' , row = 2 , col = 1)
        fig2.update_yaxes(title = 'K D RSV' , row = 3 , col = 1)
        fig2.update_yaxes(title = 'MACD' , row = 4 , col = 1)
        fig2.update_layout(
            title = "%s ~ %s (%s) 技術分析圖"%(day,day2,value),
            width = 900,
            
            height = 600
        )
        fig2.update(layout_xaxis_rangeslider_visible = False)
        fig2.show()
        pic=fig2.to_json()
        return render_template('search.html',username=username,password=password,pic=pic)
    return render_template('search.html',username=username,password=password)

@app.route("/history",methods = ["GET","POST"])
def history():
    cur = connection2.cursor()
    username=session.get('username')
    password=session.get('password')
    if request.method == "POST":
        value=request.form['number']
        day=request.form['day1']
        day2=request.form['day2']
        df = pd.DataFrame()
        time=day[0]+day[1]+day[2]+day[3]+day[5]+day[6]+day[8]+day[9]
        time2=day2[0]+day2[1]+day2[2]+day2[3]+day2[5]+day2[6]+day2[8]+day2[9]
        print(value,time,time2)
        try:
            commend = "SELECT * FROM %s_10年 WHERE 日期 BETWEEN %s AND %s"%(value,time,time2)
            cur.execute(commend)
            result = cur.fetchall()
            #print(result)#股票資料
            print(result)
        except Exception as e:
            message="資料不存在"
            return render_template('history.html',message=message)
        df = df.append(result,ignore_index = True)
        for col in [0,1,2,3,4,5,6,8]:
            for row in range(df.shape[0]):
                if col!=0:
                    df.iloc[row,col] = float(df.iloc[row,col].replace(',',''))
        
        df.columns = ['日期','成交股數','成交金額','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
        print(df)
        df.to_csv("stock_info.csv",index=False,encoding="utf_8_sig")
        #test=request(send_file("1101.csv"))
        #print(result2[:,1])#公司名稱

        return render_template('history.html',df=result,xx=value,username=username)

    return render_template('history.html',username=username,password=password)

@app.route('/download')
def download():
    return send_file("stock_info.csv")

@app.route("/test",methods = ["GET","POST"])
def test():
    curs = connection3.cursor()
    username=session.get('username')
    password=session.get('password')
    if request.method == "POST":
        request.form.get("name", False)
        dd=request.form['slt1']
        if dd=="#tab_1":
            dd=str("化學工業")
        elif dd=="#tab_2":
            dd=str("水泥工業")
        elif dd=="#tab_3":
            dd=str("半導體業")
        elif dd=="#tab_4":
            dd=str("生技醫療業")
        elif dd=="#tab_5":
            dd=str("光電業")
        elif dd=="#tab_6":
            dd=str("汽車工業")
        elif dd=="#tab_7":
            dd=str("其他業")
        elif dd=="#tab_8":
            dd=str("其他電子業")
        elif dd=="#tab_9":
            dd=str("油電燃氣業")
        elif dd=="#tab_10":
            dd=str("金融保險業")
        elif dd=="#tab_11":
            dd=str("建材營造業")
        elif dd=="#tab_12":
            dd=str("玻璃陶瓷業")
        elif dd=="#tab_13":
            dd=str("食品工業")
        elif dd=="#tab_14":
            dd=str("紡織纖維")
        elif dd=="#tab_15":
            dd=str("航運業")
        elif dd=="#tab_16":
            dd=str("通信網路業")
        elif dd=="#tab_17":
            dd=str("造紙工業")
        elif dd=="#tab_18":
            dd=str("貿易百貨業")
        elif dd=="#tab_19":
            dd=str("塑膠工業")
        elif dd=="#tab_20":
            dd=str("資訊服務業")
        elif dd=="#tab_21":
            dd=str("電子通路業")
        elif dd=="#tab_22":
            dd=str("電子零組件業")
        elif dd=="#tab_23":
            dd=str("電腦及周邊設備業")
        elif dd=="#tab_24":
            dd=str("電器電纜")
        elif dd=="#tab_25":
            dd=str("電機機械")
        elif dd=="#tab_26":
            dd=str("橡膠工業")
        elif dd=="#tab_27":
            dd=str("鋼鐵工業")
        elif dd=="#tab_28":
            dd=str("觀光事業")
        commend2 = "SELECT * FROM all_stock WHERE 產業 = '%s'"%(dd)
        curs.execute(commend2)
        result2 = curs.fetchall()
        result2=numpy.array(result2)
        print(result2)
        xz=0
        d= [range(row) for _ in range(len(result2))]
        for xz in range(0,len(result2)):
            d[xz]=result2[xz,0]+result2[xz,1]
            xz=xz+1
        print(d)
        connection3.close()
        return render_template('test.html',username=username,password=password,df=d)
    return render_template('test.html',username=username,password=password)


'''
@app.route("/data")
def data():

    
    cur = connection2.cursor()
    username=session.get('username')
    password=session.get('password')
    email=session.get('email')
    #...............................輸入時間................................................

    start_year = int(input())
    start_month = int(input())
    end_year = int(input())
    end_month = int(input())
    stock_code = int(input())
    start_date = str(date(start_year,start_month,1))
    end_date = str(date(end_year,end_month,1))
    
    
    df.columns = ['日期','成交股數','成交金額','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
    df.to_csv("%d.csv"%stock_code,index=False,encoding="utf_8_sig")
    
    df["成交量增減"] = df['成交股數'].diff()   #9
    df['成交量顏色'] = ''    #10
    df.insert(11,"RSV",'')   #11
    
#.......................................................交易良顏色判斷........................................................
    for row in range(df.shape[0]):
        if row!=0:
            if (df.iloc[row,6]>df.iloc[row-1,6]):
                df.iloc[row,10] = 'red'
            elif(df.iloc[row,6]==df.iloc[row-1,6]):
                df.iloc[row,10] = 'gray'
            elif(df.iloc[row,6]<=df.iloc[row-1,6]):
                df.iloc[row,10] = 'green'
        else:
            df.iloc[row,10] = 'red'
#....................................................算RSV.....................................................
    for row in range(df.shape[0]):                  
        if row >= 8:
            min_day = df.iloc[row,5]
            max_day = df.iloc[row,4]
            for num in range(row-8,row+1):
                if (df.iloc[num,5]<=min_day):
                    min_day = df.iloc[num,5]
                if (df.iloc[num,4]>=max_day):
                    max_day = df.iloc[num,4]
            df.iloc[row,11] = ((df.iloc[row,6]-min_day)/(max_day-min_day))*100
            df.iloc[row,11] = round(df.iloc[row,11],2)

#.....................................................算 K  D........................................................

    df['K'] = ''      #[row,12]
    df['D'] = ''       #[row,13]
    for row in range(df.shape[0]):          
        if row == 8:
            df.iloc[row,12] = (50*2/3) + (df.iloc[row,11]/3)
            df.iloc[row,13] = (50*2/3) + (df.iloc[row,12]/3)
        elif row>8:
            df.iloc[row,12] = round(((df.iloc[row-1,12]*2/3) + (df.iloc[row,11]/3)),2)
            df.iloc[row,13] = round(((df.iloc[row-1,13]*2/3) + (df.iloc[row,12]/3)),2)

#..................................................均線..........................................................

    df['MA5'] = df['收盤價'].rolling(5).mean()    #  均線[row,14]
    df['MA20'] = df['收盤價'].rolling(20).mean()   #均線[row,15] 
    df['MA60'] = df['收盤價'].rolling(60).mean()    #均線[row,16]

#..............................................計算MACD.........................................................
    df["EMA12"] = df["收盤價"].ewm(span = 12 , adjust = False).mean()    #17
    df["EMA26"] = df["收盤價"].ewm(span = 26 , adjust = False).mean()    #18 
    df["DIF"] = df["EMA12"] - df["EMA26"]                                #19
    df["MACD"] = df["DIF"].ewm(span = 9, adjust = False).mean()          #20
    df["OSC"] = df["DIF"] - df["MACD"]                                   #21
    
    #.............................................計算OSC(柱狀圖)..........................................................
    #df['OSC'] = df['DIF'] - df['MACD']                     
    
    df.insert(22,"OSC_color",'')
    for i in range(df["OSC"].shape[0]):
        if df.iloc[i,21]>=0:
            df.iloc[i,22] = 'red'
        else:
            df.iloc[i,22]  ='green'
    
#..............................................................................................................
    fig = make_subplots(
        rows = 2,
        cols = 1,
        shared_xaxes = True,  #共享X軸
        vertical_spacing = 0.05,    #子圖間隔
        row_width = [0.25,0.65])

    #...................................................K線圖....................................................

    fig.add_trace(go.Candlestick(                                       
                                x = df['日期'],
                                open = df['開盤價'],
                                high = df['最高價'],
                                low = df['最低價'],
                                close = df['收盤價'],
                                increasing_line_color = 'red',
                                decreasing_line_color = 'green',
                                name ='K線圖'),
                row = 1,
                col = 1)
    #.....................................................均線...........................................................
    fig.add_trace(go.Scatter(
                            x = df['日期'],
                            y = df['MA5'],
                            line = dict(color = 'blue' , width = 1),
                            name = 'MA5',
                            mode = 'lines'),
                row = 1,
                col = 1)
    
    fig.add_trace(go.Scatter(
                            x = df['日期'],
                            y = df['MA20'],
                            line = dict(color = 'orange' , width = 1),
                            name = 'MA20',
                            mode = 'lines'),
                row = 1,
                col = 1)

    fig.add_trace(go.Scatter(
                            x = df['日期'],
                            y = df['MA60'],
                            line = dict(color = 'green' , width = 1),
                            name = 'MA60',
                            mode = 'lines'),
                row = 1,
                col = 1)            
#..............................................................交易量............................................................

    fig.add_trace(go.Bar(                               
                        x = df['日期'],
                        y = df['成交股數'],
                        showlegend = False,
                        name = '成交股數',
                        marker_color = df["成交量顏色"]),
                row = 2,
                col = 1)
#...............................................KD值..RSV................................................................

    """fig.add_trace(go.Scatter(                               
                            x = df['日期'],
                            y = df['RSV'],
                            line = dict(color = 'gray' , width = 1),
                            name = 'RSV'),
                row = 2,
                col = 1)
    fig.add_trace(go.Scatter(
                            x = df['日期'],
                            y = df['K'],
                            line = dict(color = 'red', width = 1),
                            name = 'K9',
                            mode = 'lines'),
                row = 2,
                col = 1)
    fig.add_trace(go.Scatter(
                            x = df['日期'],
                            y = df['D'],
                            line = dict(color = 'green', width = 1),
                            name = 'D9',
                            mode = 'lines'),
                row = 2,
                col = 1)"""

#.............................................MACD(平滑異同移動平均線指標)...................................

    """fig.add_trace(go.Scatter(
                            x = df['日期'],
                            y = round(df['MACD'],2),
                            line = dict(color = 'blue', width = 1),
                            name = 'MACD',
                            mode = 'lines',),
                row = 2,
                col = 1)
    fig.add_trace(go.Scatter(
                            x = df['日期'],
                            y = round(df['DIF'],2),
                            line = dict(color = 'orange', width = 1),
                            name = 'DIF',
                            mode = 'lines',),
                row = 2,
                col = 1)
    fig.add_trace(go.Bar(
                            x = df['日期'],
                            y = round(df['OSC'],2),
                            name = 'OSC',
                            marker_color = df["OSC_color"]),
                row = 2,
                col = 1) """
               
#...............................................圖標題.......................................................  

    fig.update_xaxes(rangebreaks = [{'pattern' : 'day of week', 'bounds' : [6,1]}])
    fig.update_xaxes(title = '日期' , row = 3 , col = 1)
    fig.update_yaxes(title = '股價' , row = 1 , col = 1)
    fig.update_layout(
        title = "%d/%d ~ %d/%d %s(%d) 技術分析圖"%(start_year,start_month,end_year,end_month,stock_code),
        width = 900,
        height = 600
    )
    fig.update(layout_xaxis_rangeslider_visible = False)
    fig.show()
    
    return render_template('test.html',username=username,password=password,df=d) '''