import requests, datetime, time, zipfile, io, sys, os#, warnings, threading
import numpy as np
import pandas as pd
import mplfinance as fplt
import PySimpleGUI as sg

pd.options.display.expand_frame_repr = False # Отключаем перенос строк в выводе pandas DataFrame
pd.set_option('display.max_columns', None,'display.max_colwidth', None,'display.max_rows', None) # Устанавливаем максимальное количество отображаемых столбцов, ширину столбца и количество строк
pd.set_option('display.float_format', '{:.2f}'.format) # Устанавливаем формат отображения чисел с плавающей точкой
gaps=['1min','3min','5min','15min','30min','60min','240min'] # Определяем список интервалов времени
gap=['1m','3m','5m','15m','30m','60m','240m'] # Определяем список интервалов времени
coins=['BTCUSDT']
file='D:/Program Files/ABBYY FineReader 10/WPy64-31160/aad/history/BTCEUR-1s-2023-03.csv'
#file='BTCEUR-1m-2023-02.csv' # Определяем путь к файлу с данными
def Open(x): # Определение функции Open, которая открывает и читает файл
    with open(x, 'rt') as f: # Открываем файл в режиме чтения текста
        return [s.rstrip() for s in f] # Возвращаем список строк файла, удаляя пробельные символы справа
def Save(x, y): # Определение функции Save, которая записывает данные в файл
    with open(y, 'wt') as f: # Открываем файл в режиме записи текста
        return [f.write(s + '\n') for s in x] # Записываем каждый элемент списка x в файл, добавляя символ новой строки
def Epr(*x):
    sg.eprint(x, size=(130,30), location=(25,240))
def MLpr(x):
    window['-ML1-'].print(x)
query,doit = Open('query.txt'),Open('doit.txt') # Читаем данные из файлов 'query.txt' и 'doit.txt' и присваиваем их переменным query и doit
def File(x): # Определяем функцию File для чтения данных из файла
    if x[-3:]=='zip': # Если файл является архивом zip
        df=pd.read_csv(io.BytesIO(zipfile.ZipFile(x, mode='r').read(zipfile.ZipFile(x, mode='r').namelist()[0])))
    if x[-3:]=='uet': # Если файл имеет расширение uet
        df=pd.read_parquet(x, usecols=[0, 1, 2, 3, 4, 5, 8])
    else: # В остальных случаях
        df=pd.read_csv(x, usecols=[0, 1, 2, 3, 4, 5, 8])
    df.columns=['time', 'open', 'high', 'low', 'close', 'volume', 'num'] # Устанавливаем названия столбцов
    df.time = df.time/1000 + (3 * 60 * 60) # Преобразуем время
    df.time = pd.to_datetime(df.time, unit='s') # Преобразуем время в формат datetime
    df = df.set_index('time') # Устанавливаем столбец time в качестве индекса
    return df # Возвращаем DataFrame
def Url1(x,y):
    data=[]
    q=1000
    API_URL = f"https://api.binance.com/api/v1/klines?symbol={x}&limit={q}&interval={y}"
    r = requests.get(API_URL)
    r_json = r.json() #return r_json[-1]
    for f in range(int(q)):
        r_json[f][-1]=q
    data.extend (r_json)
    df=pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', '7', '8', 'num', '10', '11','12'], index=None)
    df.drop(['7','8','10','11','12'], axis= 1 , inplace= True )#удаляем навсегда ненужные колонки
    df=df.drop_duplicates(subset=['time']).astype(float)
    df.time=df.time/1000 + (3 * 60 * 60)#преобразовываем в datetime64
    df.time=pd.to_datetime(df.time, unit='s')#.dt.strftime("%H:%M (%d.%m.%y)")#  df.index=df.time
    df=df.set_index('time')
    return df
def newT(x,y): # Определение функции newT, которая изменяет интервал данных
    return x.resample(y).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'num': 'sum'}) # Производим ресемплирование данных с агрегацией
def Plot (start,end,t=1): # Определение функции Plot, которая строит график
    df = File(file) # Читаем файл и преобразуем его в DataFrame
    e_start = max(0, start-(t*20))  # Устанавливаем начальное значение, убеждаясь, что оно не меньше 0
    e_end = min(len(df), end+(t*50))  # Устанавливаем конечное значение, убеждаясь, что оно не больше длины df
    a= df.iloc[e_start:e_end].resample(str(t)+'min').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'num': 'sum'}) # Производим ресемплирование данных с агрегацией
    b=(a.nlargest(1,'open').index, a.nsmallest(1,'close').index) # Получаем индексы строк с наибольшим и наименьшим значением 'open'
    marker = [a.open[i] if str(i) in b else np.nan for i in a.index] # Создаем список маркеров
    addplot = fplt.make_addplot(marker, type='scatter', markersize=100, marker='>', color='g') # Создаем дополнительный график
    fplt.plot(a, type='candle', volume=True, panel_ratios=(6,1), mav=(7,21,99), addplot=addplot) # Строим график
def DictFilter(event): # Функция DictFilter обрабатывает события, связанные с выпадающим списком "Filter"
    if event == 'Add': # Если выбрано событие "Add"
        query.append(values['-FILTER-']) # Добавляем значение из поля '-FILTER-' в список query
        window['-FILTER-'].update(values=query) # Обновляем выпадающий список 'Filter' новыми значениями
    if event == 'Save': # Если выбрано событие "Save"
        Save(query,'query.txt') # Сохраняем список query в файл 'query.txt'
    if event == 'Del': # Если выбрано событие "Del"
        query.remove(values['-FILTER-']) # Удаляем значение из списка query
        window['-FILTER-'].update(values=query) # Обновляем выпадающий список 'Filter'
def DictDoit(event): # Функция DictDoit обрабатывает события, связанные с выпадающим списком "Beep"
    # Обработка событий аналогична функции DictFilter, но для списка doit и поля '-DOIT-'
    if event == 'Addd':
        doit.append(values['-DOIT-'])
        window['-DOIT-'].update(values=doit)#, value=values['-DOIT-']
    if event == 'Saved':
        Save(doit,'doit.txt')
    if event == 'Deld':
        doit.remove(values['-DOIT-'])
        window['-DOIT-'].update(values=doit)
# Определение структуры GUI
# Layout1 - это структура первой вкладки GUI. Здесь идут элементы управления, которые будут на первой вкладке# Например, sg.Text('Текст'), sg.Input('Ввод'), sg.Button('Кнопка') и т.д.
layout1=[[sg.Button('Filter'),sg.Button('Add'),sg.Button('Del'),sg.Button('Save'),sg.Combo(query,font=('Calibri', 14), key='-FILTER-', enable_events=True, s=50,expand_x=True)],
         [sg.Button('Test'),sg.Text('ma'),sg.InputText('14',key='-AVR-',s=5),sg.Text('delta_avr'),sg.InputText('1.0005',key='-DAVR-',s=8),
          sg.Text('delta_num'),sg.InputText('1.5',key='-DNUM-',s=5),sg.Text('profit'),sg.InputText('1.07',key='-PROFIT-',s=6),sg.Button('Cl')],
         [sg.Button('Do_it'),sg.Button('Addd'),sg.Button('Deld'),sg.Button('Saved'),sg.Text('Do_it'), sg.Combo(doit,font=('Calibri', 14), key='-DOIT-', enable_events=True, s=50,expand_x=True)],
         [sg.Multiline(font=('Calibri', 14),size=(150,20), key='-ML1-', autoscroll=True, reroute_stdout=True, write_only=True,
          reroute_cprint=True)],
         [sg.Button('Default'),sg.Text('File'),sg.Input(key='-FILE-', expand_x=True), sg.FileBrowse(), sg.Text('Gaps'),sg.Combo(gaps,enable_events=True,  readonly=False, key='-GAPS-',s=10),
          sg.Text('Tail'),sg.Input(key='-TAIL-',s=5),sg.Combo(coins,key='-COINS-',s=10),sg.Combo(gap,key='-GAP-',readonly=False,s=10)],
         [sg.Button('Run'),sg.Button('Url'),sg.Button('Describe'),sg.Button('Plot'),sg.Button('начало'),sg.InputText('240',key='-START-',s=5),
          sg.Button('конец'), sg.InputText('300',key='-END-',s=5),sg.Exit()]]
# Layout2 - это структура второй вкладки GUI. Здесь идут элементы управления, которые будут на второй вкладке# Например, sg.Text('Текст'), sg.Input('Ввод'), sg.Button('Кнопка') и т.д.
layout2=[[sg.Text('pro'),sg.InputText('1.07',key='-PROFIT-',s=6),sg.Button('clean')],
         [sg.Multiline(font=('Calibri', 14),size=(150,12), key='-ML2-', autoscroll=True)]]#expand_x=True, reroute_stdout=True,write_only=True, reroute_cprint=True
layout = [[sg.TabGroup([[sg.Tab('Таблицы', layout1), sg.Tab('Тест', layout2)]])]] # Layout - это общая структура GUI, которая включает в себя все вкладки. Здесь идут вкладки, которые будут в GUI. Нап��имер, sg.Tab('Вкладка 1', layout1), sg.Tab('Вкладка 2', layout2) и т.д.
window = sg.Window('Питонец by Dandr11',layout, finalize=True,resizable=True, location=(30,30),size=(1200,670)) # Создание окна GUI
dictL = {
    'Add': lambda: DictFilter('Add'),
    'Del': lambda: DictFilter('Del'),
    'Save': lambda: DictFilter('Save'),
    'Addd': lambda: DictDoit('Addd'),
    'Deld': lambda: DictDoit('Deld'),
    'Saved': lambda: DictDoit('Saved'),
    'Plot': lambda: Plot(int(values['-START-']), int(values['-END-'])),
    'Test': lambda: Test(values['-FILTER-']),
    'Do_it':lambda: MLpr(eval(values['-DOIT-'])),
    'Clean': lambda: window['-FILTER-'].update(),
    'Cl': lambda: window['-ML1-'].update(''),
    'Run': lambda: MLpr(newT(File(values['-FILE-']),values['-GAPS-']).tail(int(values['-TAIL-']))),
    'Filter': lambda: Filter(values['-FILTER-']),
    'Describe': lambda: MLpr(newT(File(values['-FILE-']),values['-GAPS-']).describe())}
def Filter(x):
    df = newT(File(values['-FILE-']),values['-GAPS-'])
    ma=int(values['-AVR-'])
    delta_ma=float(values['-DAVR-'])
    delta_num=float(values['-DNUM-'])
    d=df[eval(x)==True]
    print(d, len(d))
def Test(x):
    df = newT(File(values['-FILE-']),values['-GAPS-'])
    ma=int(values['-AVR-'])
    delta_ma=float(values['-DAVR-'])
    delta_num=float(values['-DNUM-'])
    for index, row in df[eval(x)==True].iterrows ():#
       print(index)#row['open'])
def Select(x=query):
    layout = [  [sg.Text('Select 1 or more items and click "Go"')],
                [sg.Listbox(x, key='-LB-', s=(80,20), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
                [sg.OK(), sg.Cancel()]]
    window = sg.Window('Filtres', layout)
    event, values = window.read()
    window.close()
    a=values['-LB-']
    layout = [  [sg.Text('Select 2 or more items and click "Go"')],
                [sg.Listbox(x, key='-LB1-', s=(80,20), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
                [sg.OK(), sg.Cancel()]]
    window = sg.Window('Filtres', layout)
    event, values = window.read()
    window.close()
    b=values['-LB1-']
    MLpr(a, b)
while True: # Основной цикл программы
    event, values = window.read()
    try:
        if event == sg.WIN_CLOSED or event == 'Exit':  break#window1.close() # Если событие - это закрытие окна или выбор пункта 'Exit', закрываем окно
        if event == 'Bot': os.execl(sys.executable, sys.executable, * sys.argv) # Если событие - это 'Bot', перезапускаем скрипт
        if event in dictL.keys(): dictL[event]() # Если событие находится в словарях dictR или dictP, вызываем функцию Event
        if event== 'Default': # Если событие - это 'Default', обновляем значения полей '-FILE-', '-GAPS-' и '-TAIL-'
            window['-FILE-'].update(file)
            window['-GAPS-'].update('5min')
            window['-TAIL-'].update('7')
            window['-COINS-'].update('BTCUSDT')
            window['-GAP-'].update('1m')
    except Exception as e: # Если произошла ошибка, выводим сообщение об ошибке
        sg.popup(f"Ошибка: {e}", no_titlebar = True,background_color = '#8A2BE2')
window.close()#; del window
#c1=f'(close / close.rolling(window={ma}).mean() > {delta_ma}) & (num / num.rolling(window={ma}).mean() > {delta_num})'
#c2 = f'(close / close.rolling(window={ma}).mean() < abs(2-{delta_ma})) & (num / num.rolling(window={ma}).mean() > {delta_num})'