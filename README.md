# Youtube-Highlight-Miner

自動分析 YouTube / Twitch 直播聊天室訊息，找出影片精華時刻（Highlight），並透過網頁介面直接觀看。


https://github.com/user-attachments/assets/095393d1-cd11-4dc3-8a1c-a04380c44430




## 功能簡介

- 輸入 YouTube 或 Twitch 影片網址，自動爬取聊天室訊息
- 依據聊天頻率統計，定位影片高潮片段
- **LSTM 版本**：使用深度學習模型預測精華時間點，提升準確度
- 網頁內嵌播放器，可直接跳轉至精華片段觀看
- IoT 感測器數據視覺化（溫濕度圖表）

## 專案結構

```
├── Youtube_Crawler/          # 基於聊天頻率的精華擷取版本
│   ├── app.py                # Flask 後端主程式
│   └── templates/            # 前端頁面
├── Youtube_Crawler_LSTM/     # LSTM 深度學習預測版本
│   ├── app.py                # Flask 後端（含模型推論）
│   ├── model.h5              # 預訓練 LSTM 模型
│   └── templates/            # 前端頁面
├── index_v1.html             # IoT 感測器數據視覺化頁面
└── xampp/                    # 本地伺服器環境
```

## 使用技術

| 類別 | 技術 |
|------|------|
| **Backend** | Python, Flask, PHP |
| **Frontend** | HTML / CSS / JavaScript, jQuery, YouTube IFrame API, Highcharts |
| **Database** | MySQL (PyMySQL) |
| **ML / DL** | TensorFlow, Keras (LSTM), NumPy, Pandas |
| **Web Scraping** | chat_downloader |
| **Server** | XAMPP (Apache + MySQL) |
| **Visualization** | Matplotlib, Highcharts |

## 快速開始

1. 啟動 XAMPP（Apache + MySQL）
2. 建立資料庫 `youtube_chatroom` 及使用者帳號
3. 安裝 Python 套件：
   ```bash
   pip install flask pymysql chat-downloader matplotlib tensorflow keras numpy pandas
   ```
4. 執行應用程式：
   ```bash
   # 聊天頻率版本
   python Youtube_Crawler/app.py

   # LSTM 預測版本
   python Youtube_Crawler_LSTM/app.py
   ```
5. 開啟瀏覽器前往 `http://localhost/youtube_miner`，輸入影片網址即可
