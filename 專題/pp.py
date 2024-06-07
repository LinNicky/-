import requests as r
from lxml import etree
import pandas as pd
from datetime import datetime, date
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

from fake_useragent import UserAgent
import time ,random
import numpy as ny




def get_stock_data():
#.....................................................輸入時間................................................

    start_year = int(input())
    start_month = int(input())
    end_year = int(input())
    end_month = int(input())
    stock_code = int(input())
    start_date = str(date(start_year,start_month,1))
    end_date = str(date(end_year,end_month,1))
    
    df = pd.DataFrame()
    month_list = pd.date_range(start_date,end_date,freq = 'MS').strftime("%Y%m%d").tolist()
    fake_user = UserAgent()
    for month in month_list:
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date="+month+"&stockNo="+str(stock_code)
        res = r.get(url,headers={'User-Agent':fake_user.random})
        stock_json = res.json()
        stock_df = pd.DataFrame.from_dict(stock_json['data'])
        if KeyError:
            pass
        df = df.append(stock_df,ignore_index = True)
        time.sleep(random.uniform(3,5))
    
    for col in [0,1,2,3,4,5,6,8]:
        for row in range(df.shape[0]):
            if col ==0:
                day = df.iloc[row,0].split('/')
                df.iloc[row,0] = datetime(int(day[0])+1911,int(day[1]),int(day[2]))
            elif col!=0:
                df.iloc[row,col] = float(df.iloc[row,col].replace(',',''))
    
    
    df.columns = ['日期','成交股數','成交金額','開盤價','最高價','最低價','收盤價','漲跌價差','成交筆數']
    df.to_csv("%d.csv"%stock_code,index=False,encoding="utf_8_sig")

    stock_name = (stock_json["title"][13:21])
    
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
        title = "%d/%d ~ %d/%d %s(%d) 技術分析圖"%(start_year,start_month,end_year,end_month,stock_name,stock_code),
        width = 900,
        height = 600
    )
    fig.update(layout_xaxis_rangeslider_visible = False)
    fig.show()
    
    return df 
    
print(get_stock_data())





#...................................................................................................................
"""line_chart = go.Figure(data = [go.Scatter(x = df['日期'],y = df['最高價'], name= '最高價', line = dict(width = 3)),
                                   go.Scatter(x = df['日期'],y = df['最低價'], name= '最低價', line = dict(width = 3)),
                                   go.Scatter(x = df['日期'],y = df['收盤價'], name= '收盤價', line = dict(width = 3)),])
    
    line_chart.update_xaxes(title_text = "日期")
    line_chart.update_yaxes(title_text = "股價")

    line_chart.update_layout(
        title= "%d %d月 到 %d %d月 %s歷史資料"%(start_year,start_month,end_year,end_month,stock_name),
        width = 1000,
        height = 500
    )
    line_chart.show()"""


    