import datetime,time,threading,os,sys,requests
import PySimpleGUI as sg
import pandas as pd#import numpy as np
from binance.client import Client#from binance.enums import *
from binance import ThreadedWebsocketManager
api_key='fks8FZtYN7dzh32b8Hp6fWAQBn4PIRC9kot7jZV16qL6LAd5MxV4aDPMLz4oMfkD'
api_secret='HdIsfSUMepgiFUnAP9xhQszsunf6mIgJE0ndqOvZXZCX2z4Af2ykwPVonNcHJQdu'
client=Client(api_key, api_secret, testnet=True)
list_doit=['kline','depth','kline.iloc[-1]',"depth.iloc[list(depth['time'])>=depth.time.unique()[-1]]"]
list_trading_pairs=['BTCUSDT','ETHUSDT','ETHBTC','BNBUSDT','BNBETH','BNBBTC']
list_df=['aggTrade','depth','bookTicker','ticker','kline_1s']
list_socket=['btcusdt@aggTrade','btcusdt@depth','btcusdt@bookTicker',
             'btcusdt@ticker','btcusdt@kline_1s']
kline=pd.DataFrame(columns=['time','open','high','low','close','volume', 'num'], index=None).tail(10)
#c1 = f'(close / close.rolling(window={ma}).mean() > {delta_ma}) & (num / num.rolling(window={ma}).mean() > {delta_ma})'
#c2 = f'(close / close.rolling(window={ma}).mean() < abs(2-{delta_ma})) & (num / num.rolling(window={ma}).mean() > {delta_num}))'
d=list()
layout=[[sg.Button('Run'),sg.Button('Go'),
         sg.Button('Ping'),sg.Input(key='-ping-',s=5, font=('Calibri',11)),
         sg.Button('Depth'),sg.Input(key='-depth-',s=5, font=('Calibri',11)),
         sg.Button('Bill'),sg.Input(key='-bill-',s=10, font=('Calibri',11),expand_x=True),
         sg.Combo(list_trading_pairs,key='-ltp-',default_value='BTCUSDT',s=8,font=('Calibri',11), readonly=False),
         sg.Button('Clear')],
        [sg.Button('Do_it'),sg.Combo(list_doit,key='-LIST_DOIT-',s=10,font=('Calibri',11), expand_x=True, enable_events=True)],
        [sg.Button('Best D order'),sg.Button('Buy order'),sg.Input('0.1',key='-buy-',s=5, font=('Calibri',11)),
         sg.Button('Sell order'),sg.Input('0.1',key='-sell-',s=5, font=('Calibri',11)),
         sg.Button('Del order'),sg.Button('All orders')],
        [sg.Button('Buy D order'),sg.Text('avr'),sg.InputText('14',key='-AVR-',s=5),
         sg.Text('delta_avr'),sg.InputText('1.0005',key='-DAVR-',s=8),
         sg.Text('delta_num'),sg.InputText('1.5',key='-DNUM-',s=5),
         sg.Text('profit'),sg.InputText('1.07',key='-PROFIT-',s=6), sg.Button('Default Bid')],
        [sg.Button('Sell D order'),sg.Text('avr'),sg.InputText('14',key='-AVR1-',s=5),
         sg.Text('delta_avr'),sg.InputText('1.0005',key='-DAVR1-',s=8),
         sg.Text('delta_num'),sg.InputText('1.5',key='-DNUM1-',s=5), sg.Button('Default Sell')],
        [sg.Input(key='-orders-',s=15, font=('Calibri',11),expand_x=True),],
        [sg.Multiline(size=(500,800),key='-ML-',autoscroll=True)]]#expand_x=True,enable_events=True
window=sg.Window('by Dandr11',layout, finalize=True,resizable=True, location=(10,30),size=(740,600))#.Maximize()#
def D (df=kline,ma=3,delta_ma=0.1,delta_num=2.7):
    c1=(df.close / df.close.rolling(window=ma).mean() > delta_ma) & (df.num / df.num.rolling(window=ma).mean() > delta_num)
    #return c1
    d=df[c1==True]
    return d.index
    #print(df.loc[d.index[-2]:])
def D1 (x,df=kline,ma=14,delta_ma=0.1,delta_num=3):
    c2=(df.open / df.open.rolling(window=ma).mean() < abs(2-delta_ma)) & (df.num / df.num.rolling(window=ma).mean() > delta_num)
    #return c1
    d=df.loc[x:][c2==True]
    #print (x)
    global idx
    idx = d.index[0]
    #print (idx)
    return d.index[0]
def Run():
    global twm
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()
    twm.start_kline_socket (symbol=values['-ltp-'],callback=d.append)#Go)
    #twm.start_multiplex_socket(callback=Go,streams=['btcusdt@kline_1s','btcusdt@depth'])
    twm.join()
def Go():
    #kline.loc[ len(kline.index )] = [x['data']['E']/1000, x['data']['k']['o'],x['data']['k']['h'],x['data']['k']['l'],x['data']['k']['c'],x['data']['k']['v'],x['data']['k']['n']]
    #kline['time']=pd.to_datetime(kline['time'], unit='s')
    #df=df.set_index('data.E')
    window['-ML-'].print(d[-1])#kline.tail(10))
def R(X,ma=14,delta_ma=0.5,delta_num=3):

    a=pd.DataFrame(index=None)
    for x in X.itertuples():
        #print(x)
        df1 = pd.DataFrame([x],index=None)
        a = pd.concat([a,df1])
        if len (a) == ma+1:
            a=a.iloc[1:]
        #print(a.iloc[-1].Index)
        #a1 = (a.close / a.close.rolling(window=ma).mean() > delta_ma) & (a.num / a.num.rolling(window=ma).mean() > delta_num)
        b1= a.num / a.num.rolling(window=ma).mean() < delta_num
        if a.loc[b1==True].empty==False:#df.iloc[x].loc[a==True].all() == True and df.iloc[x].loc[a==True].empty==False:
            print (len(a),'buy', a.loc[b1==True].num.value)
def Save_log(*x): # Определение функции, которая записывает данные в файл
    with open('log.txt', 'wt') as f: # Открываем файл в режиме записи текста
        f.write('\n')
        return [f.write(str(s)) for s in x] # Записываем каждый элемент списка x в файл, добавляя символ новой строки
def Event(event): # Функция Event вызывает соответствующие функции обработки в зависимости от произошедшего события
    if event in dictR: # Если событие находится в словаре dictR
        dictR[event]() # запускаем lambda для еvent из словаря dictR
        #window['-orders-'].update(f'{event} {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        #window['-ML-'].print(event,datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

def Ping():
    window['-ping-'].update(client.ping())
def Depth():
    #window['-depth-'].update(f'BTC {client.get_asset_balance(asset="BTC")["free"]}')
    pass
def Bill():
    window['-bill-'].update(f'BTC {client.get_asset_balance(asset="BTC")["free"]}')
def Best_order():
    deptH=client.get_order_book(symbol=values['-ltp-'])
    best_buy,best_sell=deptH['bids'][3][0],deptH['asks'][3][0]
    if sum([float(deptH['asks'][y][1]) for y in range (1,10)],0)<sum([float(deptH['bids'][y][1]) for y in range (1,10)],0):
        client.order_limit_buy(symbol=values['-ltp-'],quantity=values['-buy-'],price=best_buy)
    else:
        client.order_limit_sell(symbol=values['-ltp-'],quantity=values['-sell-'],price=best_sell)
    pass
def B_order():
    Save_log(client.order_market_buy(symbol=values['-ltp-'],quantity=values['-buy-']))
    pass
def S_order():
    client.order_market_sell(symbol=values['-ltp-'],quantity=values['-sell-'])
    pass
def D_order():#del_all_order():
    a=client.get_open_orders(symbol=values['-ltp-'])
    for b in [a[x]['orderId'] for x in range (len (a))]:
        client.cancel_order(symbol=values['-ltp-'],orderId=b)
    '''deptH=client.get_order_book(symbol=symbol)
    best_buy,best_sell=deptH['bids'][3][0],deptH['asks'][3][0]
    if sum([float(deptH['asks'][y][1]) for y in range (1,10)],
        0)<sum([float(deptH['bids'][y][1]) for y in range (1,10)],0):
        client.order_limit_buy(symbol=symbol,quantity=0.001,price=best_buy)
        Epr('BUY')
    else:
        client.order_limit_sell(symbol=symbol,quantity=0.001,price=best_sell)'''
    pass
def A_order():
    window['-ML-'].print(pd.DataFrame(client.get_open_orders(symbol=values['-ltp-']),
          columns=['symbol','price','side','origQty','status','type','time','orderId']))
    pass
def B_D_order():
    deptH=client.get_order_book(symbol=values['-ltp-'])
    best_buy=deptH['bids'][3][0]
    Save_log(client.order_limit_buy(symbol=values['-ltp-'],quantity=0.001,price=best_buy))
    pass
def S_D_order():
    deptH=client.get_order_book(symbol=values['-ltp-'])
    best_sell=deptH['asks'][3][0]
    client.order_limit_sell(symbol=values['-ltp-'],quantity=0.001,price=best_sell)
    pass
def Epr(x):
    sg.eprint(x, size=(84,20), location=(13,420))#print(,'\n'),no_titlebar = True
dictR = {'Go': lambda: Go(),
         'Do_it': lambda: Epr(eval(values['-LIST_DOIT-'])),
         'Ping': lambda: Ping(), #Epr(eval(values['-LIST_DOIT-'])),
         'Depth': lambda: Depth(),
         'Bill': lambda: Bill(),
         #'Rebot': lambda: os.execl(sys.executable,sys.executable,*sys.argv),
         'Best D order': lambda: Best_order(),
         'Buy order': lambda: B_order(),
         'Sell order': lambda: S_order(),
         'Del order': lambda: D_order(),
         'All orders': lambda: A_order(),
         'Buy D order': lambda: B_D_order(),
         'Sell D order': lambda: S_D_order()}
while True:
    event, values = window.read()
    try:
        if event == 'Run':
            threading.Thread(target=Run).start()
            window['-ML-'].print('Thread',datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        if event in dictR.keys(): Event(event)
        if event == sg.WIN_CLOSED: break
        if event == 'Clear':
            window['-ML-'].update('')
        if event== 'Default Bid': # Если событие - это 'Default', обновляем значения полей '-FILE-', '-GAPS-' и '-TAIL-'
            window['-AVR-'].update('14')
            window['-DAVR-'].update('1.0005')
            window['-DNUM-'].update('1.5')
            window['-PROFIT-'].update('1.07')
        if event== 'Default Sell': # Если событие - это 'Default', обновляем значения полей '-FILE-', '-GAPS-' и '-TAIL-'
            window['-AVR1-'].update('7')
            window['-DAVR1-'].update('1.05')
            window['-DNUM1-'].update('1.4')
    except Exception as e:
        sg.popup(e, no_titlebar = True,background_color = 	'#8A2BE2')