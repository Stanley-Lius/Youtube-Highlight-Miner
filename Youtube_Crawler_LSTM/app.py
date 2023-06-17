from flask import Flask, render_template, request, jsonify
import pymysql
from chat_downloader import ChatDownloader
import matplotlib.pyplot as plt
import pickle
from matplotlib.pyplot import MultipleLocator
# import vlc
# import pafy
import re
import keras
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, concatenate
from tensorflow.keras.models import load_model

app = Flask(__name__, static_folder='Youtube_Crawler')

model = load_model('./model.h5')

# 資料庫連線設定
db_host = 'localhost'
db_user = 'RunRunAIOT'
db_password = '1234'
db_name = 'youtube_chatroom'

period = 5    # sec
maintain = 1    # 5 * 6 = 30
time_back = 6     # 5 * 6 = 30 

input_url=''
url=''
mode=''
ID=''
chat_count = []#計算每個區間的留言筆數


@app.route('/youtube_miner')
def youtube_miner():
    return render_template('youtube_miner.html')


   
@app.route('/youtube_miner', methods=['POST'])
def process_input():
    global input_url 
    input_url = request.form.get('inputText')
    return render_template('youtube_miner.html',result='processing')
  
@app.route('/load')
def load():
    return render_template('load.html')

  
@app.route('/youtube_miner/load', methods=['POST', 'GET'])
def youtube_chatgpt_load():
    data = request.data
    download(input_url)     
    return "success"    

    

#def return_result(result):
   # return render_template('youtube_miner.html', result='fuck html')



# 路由: 首頁
@app.route('/youtube_miner/data')
def index():

 
    # 連接到資料庫
    connection = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name)

    # 建立游標
    cursor = connection.cursor()

    # 執行 SQL 查詢語句
    query = 'SELECT * FROM hightlight_time'
    try:
        cursor.execute(query)
         # 取得查詢結果
        results = cursor.fetchall()
    except Exception as e:
        print("Database has no sheet now!!!")
    
    # 關閉游標和資料庫連線
    cursor.close()
    connection.close()
    
    delete()
    
    # 傳遞資料到 HTML 檔案並渲染
    return jsonify(results)
      

    
    
def download(input_url):
    #抓取聊天室內容
    #url = 'https://www.youtube.com/watch?v=cD4lzId1Y9M'
    global url
    global mode
    global ID
    url = input_url
    print(ID)
    if input_url[12] == 't':
      mode = 'twitch'
    elif input_url[12] == 'y':
      mode = 'youtube'
    chat = ChatDownloader().get_chat(input_url)
    if(mode=='twitch'):
        ID = re.search(r'video/[a-z0-9]*',input_url).group()[6:]
    elif(mode=='youtube'):
        ID = re.search(r'=.*',input_url).group()[1:]
    print(input_url)
    count_chat(chat)
    
def count_chat(chat):
    print("Start working")
    timerecord = []
    #將有效的留言存入timerecord陣列中
    for message in chat:
        if message["time_in_seconds"] > 0:
            timerecord.append(message["time_in_seconds"])
    count = 0
    time_box = 1
    timecount = []#計算時間區間
    global chat_count#計算每個區間的留言筆數
    chat_count_next = []
    
    for every_time in timerecord:
        #如果留言時間所在區間大於time_box
      while every_time / period > time_box:
        timecount.append({"time" : f"{int((time_box - 1) / (3600 / period))}".zfill(1) + ":" + f"{int((time_box - 1) / (60 / period) % 60)}".zfill(2) + ":" + f"{int((time_box - 1) % (60 / period) * period)}".zfill(2), "time_box": time_box})
        chat_count.append(count)
        chat_count_next.append(count)      
        count = 0
        time_box = time_box + 1
      count = count + 1
    timecount.append({"time" : f"{int((time_box - 1) / (3600 / period))}".zfill(1) + ":" + f"{int((time_box - 1) / (60 / period) % 60)}".zfill(2) + ":" + f"{int((time_box - 1) % (60 / period) * period)}".zfill(2), "time_box": time_box})
    chat_count.append(count)
    chat_count_next.append(count)
 
    for i in range(maintain):
      chat_count_next.append(0)
      chat_count_next.pop(0)
      for j in range(len(chat_count)):
        chat_count[j] = chat_count[j] + chat_count_next[j]
    for i in range(len(chat_count)):
       
      (timecount[i]).update({"chat_count" : chat_count[i]})
    print("Finish")
    #show(timecount)
    data_preprocess(timecount)
    
    
def data_preprocess(timecount):
    x = []
    y = []
    for i in range(len(timecount)):
      x.append(timecount[i]["time"])
      y.append(timecount[i]["chat_count"])
    slope = []
    for i in range(len(x)):
      if i == 0:
        if float(y[0]) == 0:
          slope.append(1)
        else:
          slope.append(float(y[1])/float(y[0]))
      else:
        if float(y[i-1]) == 0:
          slope.append(1)
        else:
          slope.append(float(y[i])/float(y[i-1]))
    data = pd.DataFrame({'時間': x, '數量': y, '斜率': slope})
    X1 = np.array(data['數量']).reshape(-1, 1)
    X2 = np.array(data['斜率']).reshape(-1, 1)
    X1 = np.reshape(X1, (X1.shape[0], X1.shape[1], 1))
    X2 = np.reshape(X2, (X2.shape[0], X2.shape[1], 1))

    # 預測結果
    predictions = model.predict([X1, X2])
    predicted_labels = (predictions > 0.22).astype(int)
    
    # 找到預測結果為1的時間點
    predicted_times = data['時間'][predicted_labels.flatten() == 1]

    print("預測結果為1的時間點：")
    print(predicted_times)
    
    for i in range(len(chat_count)):
      (timecount[i]).update({"prediction" : predictions[i][0]})
    predict_indexs = []
    for predicted_time in predicted_times:
      predict_indexs.append(x.index(predicted_time))
    sorting(timecount)
    
    
def show(timecount):
    x = []
    y = []
    for i in range(len(timecount)):
      x.append(timecount[i]["time"])
      y.append(timecount[i]["chat_count"])
    plt.figure(figsize = (80,6))
    plt.bar(range(len(x)), y, tick_label = x)
    plt.gca().xaxis.set_major_locator(MultipleLocator((60 / period) * 6))
    plt.show()
    
def get_count(element):
  return element['prediction']
  
def sorting(timecount):
    clip_number = 10
    clip_time_count = 0
    
    timecount.sort(reverse=True, key=get_count)
    clip_countdown = 10
    clip_time_set = set()
    
    while(clip_countdown > 0):
      clip_time_dicts_count = len(clip_time_set)
      now_dict = timecount[clip_time_count]['time_box']
      clip_time_count = clip_time_count + 1
      now_time_box = set([i for i in range(now_dict-10, now_dict -3)])
      if (now_dict - 10 in clip_time_set) and (now_dict - 3 in clip_time_set):
        check = False
        for time in now_time_box:
          if time not in clip_time_set:
            check = True
            break
        if check == True:
          clip_countdown = clip_countdown + 1
      elif (now_dict - 10 not in clip_time_set) and (now_dict - 3 not in clip_time_set):
        clip_countdown = clip_countdown - 1
      clip_time_set = ( clip_time_set | now_time_box )
    clip_time_set = sorted(clip_time_set)
    answer(timecount, clip_time_set)
    
    
def answer(timecount, clip_time_set):
    clip_time_final = []
    video_urls = []
    HLtime = []
    global chat_count
    for i in range(10):
      clip_start = 0
      clip_end = 0
      if clip_end + 1 < len(clip_time_set):
        while(clip_time_set[clip_end + 1] == clip_time_set[clip_end] + 1):
          clip_end = clip_end + 1
          if(clip_end == len(clip_time_set) - 1):
            break
      else:
        print("error break")
        break
      clip_time_final.append([f"{int((clip_time_set[clip_start]) / (3600 / period))}".zfill(1) + ":" + f"{int((clip_time_set[clip_start]) / (60 / period) % 60)}".zfill(2) + ":" + f"{int((clip_time_set[clip_start]) % (60 / period) * period)}".zfill(2),
                  f"{int((clip_time_set[clip_end] + 1) / (3600 / period))}".zfill(1) + ":" + f"{int((clip_time_set[clip_end] + 1) / (60 / period) % 60)}".zfill(2) + ":" + f"{int((clip_time_set[clip_end] + 1) % (60 / period) * period)}".zfill(2),
                  url + ('&' if mode == 'youtube' else '?') + f"t={(clip_time_set[clip_start]  if (clip_time_set[clip_start] >= 0) else 0) * period}s", (clip_time_set[clip_start]  if (clip_time_set[clip_start] >= 0) else 0) * period])
      if (clip_time_set[clip_start] >= 0) :
        HLtime.append([clip_time_set[clip_start] * period, (clip_time_set[clip_end]+1) * period])
      elif (clip_time_set[clip_start] <= 0):
        HLtime.append([0, 0])
      clip_length = clip_end - clip_start + 1
      for i in range(clip_length):
        clip_time_set.pop(clip_start)
      
    for i in range(len(clip_time_final)):
      print(f"clip " + f"{i+1}".zfill(2) + f": {clip_time_final[i][0]} ~ {clip_time_final[i][1]}" + "  " + clip_time_final[i][2])
    chat_count =[]
    save(HLtime, clip_time_final)
    
  

def save(HLtime, clip_time_final):
    # Connect to MySQL database
    db = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = db.cursor()
    
    # Create a table to store chat records (if it doesn't exist)
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS hightlight_time (
            id INT PRIMARY KEY,
            videoID VARCHAR(32),
            time_begin VARCHAR(8),
            time_end VARCHAR(8),
            time_begin_str VARCHAR(16),
            time_end_str VARCHAR(16),
            mode VARCHAR(8)
        )
    '''
    cursor.execute(create_table_query)
    db.commit()
    try:
    # Insert chat records into MySQL database
        for i in range(len(HLtime)):
            time_begin = HLtime[i][0]
            time_end = HLtime[i][1]
            insert_query = '''
                INSERT INTO hightlight_time (id, videoID, time_begin, time_end, time_begin_str, time_end_str, mode)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (i, ID, time_begin, time_end, clip_time_final[i][0], clip_time_final[i][1], mode))
            db.commit()
    except Exception as e:
        print("Error inserting chat records:", str(e))
    # Close the database connection
    db.close()

def delete():
    db = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = db.cursor()
    try:
        sql_delete = '''
            DELETE FROM hightlight_time
        '''
        cursor.execute(sql_delete)
        db.commit()
    except Exception as e:
        print("Error delete chat records:", str(e))
     #Close the database connection
    db.close()

    
    
if __name__ == '__main__':
    app.run(port=80)
    
    
   
