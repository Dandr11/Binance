import datetime,threading#,time,os,sys,requests
import PySimpleGUI as sg
import pandas as pd#import numpy as np
from binance.client import Client#from binance.enums import *
from binance import ThreadedWebsocketManager
api_key='fks8FZtYN7dzh32b8Hp6fWAQBn4PIRC9kot7jZV16qL6LAd5MxV4aDPMLz4oMfkD'
api_secret='HdIsfSUMepgiFUnAP9xhQszsunf6mIgJE0ndqOvZXZCX2z4Af2ykwPVonNcHJQdu'
client=Client(api_key, api_secret, base_url='https://testnet.binance.vision')
list_doit=['kline','depth','kline.iloc[-1]',"depth.iloc[list(depth['time'])>=depth.time.unique()[-1]]"]
list_trading_pairs=['BTCUSDT','ETHUSDT','ETHBTC','BNBUSDT','BNBETH','BNBBTC']
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

def Run():
    global twm
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()
    twm.start_kline_socket (symbol=values['-ltp-'],callback=d.append)#Go)
    #twm.start_multiplex_socket(callback=Go,streams=['btcusdt@kline_1s','btcusdt@depth'])
    twm.join()
def Go(x):
    kline.loc[ len(kline.index )] = [x['E']/1000, x['k']['o'],x['k']['h'],x['k']['l'],x['k']['c'],x['k']['v'],x['k']['n']]
    kline['time']=pd.to_datetime(kline['time'], unit='s')#df=df.set_index('data.E')
    window['-ML-'].print(d[-11:-1])#kline.tail(10))
def Depth():
    window['-ML-'].print(f'BTC {client.depth(asset="BTC")["free"]}')
def Bill():
    window['-bill-'].update(f'BTC {client.account(asset="BTC")["free"]}')
def Best_order():
    deptH=client.get_order_book(symbol=values['-ltp-'])
    best_buy,best_sell=deptH['bids'][3][0],deptH['asks'][3][0]
    if sum([float(deptH['asks'][y][1]) for y in range (1,10)],0)<sum([float(deptH['bids'][y][1]) for y in range (1,10)],0):
        client.order_limit_buy(symbol=values['-ltp-'],quantity=values['-buy-'],price=best_buy)
    else:
        client.order_limit_sell(symbol=values['-ltp-'],quantity=values['-sell-'],price=best_sell)
    #pass
def B_order():
    #Save_log(client.order_market_buy(symbol=values['-ltp-'],quantity=values['-buy-']))
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
    client.order_limit_buy(symbol=values['-ltp-'],quantity=0.001,price=best_buy)
    pass
def S_D_order():
    deptH=client.get_order_book(symbol=values['-ltp-'])
    best_sell=deptH['asks'][3][0]
    client.order_limit_sell(symbol=values['-ltp-'],quantity=0.001,price=best_sell)
    pass
def Epr(x):
    sg.eprint(x, size=(84,20), location=(13,420))#print(,'\n'),no_titlebar = True
dictL = {'Go': lambda: Go(),
         'Do_it': lambda: Epr(eval(values['-LIST_DOIT-'])),
         #'Ping': lambda: Ping(), #Epr(eval(values['-LIST_DOIT-'])),
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
        if event in dictL.keys(): dictL[event]()
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