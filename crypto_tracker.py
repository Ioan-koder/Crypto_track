import tkinter as tk
from tkinter import ttk, messagebox
import websocket
import json
import threading
import time
from datetime import datetime
import requests
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math

class CyberpunkCryptoTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CYBERPUNK CRYPTO TRACKER v2.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        
        # Цветовая схема киберпанк
        self.colors = {
            'bg_dark': '#0a0a0a',
            'bg_medium': '#1a1a1a',
            'bg_light': '#2a2a2a',
            'neon_blue': '#00ffff',
            'neon_pink': '#ff00ff',
            'neon_green': '#00ff00',
            'neon_yellow': '#ffff00',
            'text_white': '#ffffff',
            'text_gray': '#888888'
        }
        
        # Список криптовалют
        self.crypto_data = {
            'BTC': {'symbol': 'btcusdt', 'name': 'Bitcoin', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'ETH': {'symbol': 'ethusdt', 'name': 'Ethereum', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'XRP': {'symbol': 'xrpusdt', 'name': 'Ripple', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'TAO': {'symbol': 'taousdt', 'name': 'Bittensor', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'ADA': {'symbol': 'adausdt', 'name': 'Cardano', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'FET': {'symbol': 'fetusdt', 'name': 'Fetch.ai', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'RUNE': {'symbol': 'runeusdt', 'name': 'ThorChain', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'DYDX': {'symbol': 'dydxusdt', 'name': 'dYdX', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'LINK': {'symbol': 'linkusdt', 'name': 'Chainlink', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'DOT': {'symbol': 'dotusdt', 'name': 'Polkadot', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'AAVE': {'symbol': 'aaveusdt', 'name': 'Aave', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0},
            'GRT': {'symbol': 'grtusdt', 'name': 'The Graph', 'price_usd': 0, 'price_rub': 0, 'change_24h': 0, 'change_30d': 0}
        }
        
        self.usd_rub_rate = 0
        self.last_update = "Ожидание..."
        self.websocket_connected = False
        
        self.setup_ui()
        self.start_data_fetch()
        
    def setup_ui(self):
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        title_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="CRYPTO TRACKER", 
                              font=('Courier', 20, 'bold'), 
                              fg=self.colors['neon_blue'], 
                              bg=self.colors['bg_dark'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="REAL-TIME MONITORING", 
                                 font=('Courier', 9), 
                                 fg=self.colors['text_gray'], 
                                 bg=self.colors['bg_dark'])
        subtitle_label.pack()
        
        # Статус бар
        status_frame = tk.Frame(main_frame, bg=self.colors['bg_medium'], height=40)
        status_frame.pack(fill='x', pady=(0, 20))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="INITIALIZING...", 
                                    font=('Courier', 10), 
                                    fg=self.colors['neon_green'], 
                                    bg=self.colors['bg_medium'])
        self.status_label.pack(side='left', padx=10, pady=10)
        
        self.time_label = tk.Label(status_frame, text="", 
                                  font=('Courier', 10), 
                                  fg=self.colors['text_gray'], 
                                  bg=self.colors['bg_medium'])
        self.time_label.pack(side='right', padx=10, pady=10)
        
        # Контейнер для карточек криптовалют
        cards_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        cards_frame.pack(fill='both', expand=True)
        
        # Создание карточек для каждой криптовалюты
        self.crypto_cards = {}
        row = 0
        col = 0
        for crypto, data in self.crypto_data.items():
            card = self.create_crypto_card(cards_frame, crypto, data)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            self.crypto_cards[crypto] = card
            col += 1
            if col > 3:  # 4 карточки в ряд для лучшего размещения
                col = 0
                row += 1
        
        # Настройка весов для адаптивности
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):  # 3 ряда для 12 криптовалют (4x3 = 12)
            cards_frame.grid_rowconfigure(i, weight=1)
        
        # Обновление времени
        self.update_time()
        
    def create_crypto_card(self, parent, crypto, data):
        # Создание карточки криптовалюты
        card_frame = tk.Frame(parent, bg=self.colors['bg_medium'], 
                             relief='raised', bd=2, highlightthickness=1,
                             highlightbackground=self.colors['neon_blue'])
        
        # Заголовок карточки
        header_frame = tk.Frame(card_frame, bg=self.colors['bg_light'])
        header_frame.pack(fill='x', padx=5, pady=5)
        
        crypto_label = tk.Label(header_frame, text=crypto, 
                               font=('Courier', 14, 'bold'), 
                               fg=self.colors['neon_blue'], 
                               bg=self.colors['bg_light'])
        crypto_label.pack(side='left', padx=10, pady=5)
        
        name_label = tk.Label(header_frame, text=data['name'], 
                             font=('Courier', 9), 
                             fg=self.colors['text_gray'], 
                             bg=self.colors['bg_light'])
        name_label.pack(side='right', padx=10, pady=5)
        
        # Цены
        prices_frame = tk.Frame(card_frame, bg=self.colors['bg_medium'])
        prices_frame.pack(fill='x', padx=10, pady=5)
        
        # USD цена
        usd_frame = tk.Frame(prices_frame, bg=self.colors['bg_medium'])
        usd_frame.pack(fill='x', pady=2)
        
        usd_label = tk.Label(usd_frame, text="USD:", 
                            font=('Courier', 11), 
                            fg=self.colors['text_gray'], 
                            bg=self.colors['bg_medium'])
        usd_label.pack(side='left')
        
        self.usd_price_labels = getattr(self, 'usd_price_labels', {})
        self.usd_price_labels[crypto] = tk.Label(usd_frame, text="$0.0000", 
                                                font=('Courier', 12, 'bold'), 
                                                fg=self.colors['neon_green'], 
                                                bg=self.colors['bg_medium'])
        self.usd_price_labels[crypto].pack(side='right')
        
        # RUB цена
        rub_frame = tk.Frame(prices_frame, bg=self.colors['bg_medium'])
        rub_frame.pack(fill='x', pady=2)
        
        rub_label = tk.Label(rub_frame, text="RUB:", 
                            font=('Courier', 11), 
                            fg=self.colors['text_gray'], 
                            bg=self.colors['bg_medium'])
        rub_label.pack(side='left')
        
        self.rub_price_labels = getattr(self, 'rub_price_labels', {})
        self.rub_price_labels[crypto] = tk.Label(rub_frame, text="₽0.00", 
                                                font=('Courier', 12, 'bold'), 
                                                fg=self.colors['neon_yellow'], 
                                                bg=self.colors['bg_medium'])
        self.rub_price_labels[crypto].pack(side='right')
        
        # Изменение за 24ч
        change_frame = tk.Frame(card_frame, bg=self.colors['bg_medium'])
        change_frame.pack(fill='x', padx=10, pady=5)
        
        change_label = tk.Label(change_frame, text="24h:", 
                               font=('Courier', 10), 
                               fg=self.colors['text_gray'], 
                               bg=self.colors['bg_medium'])
        change_label.pack(side='left')
        
        self.change_labels = getattr(self, 'change_labels', {})
        self.change_labels[crypto] = tk.Label(change_frame, text="0.00%", 
                                             font=('Courier', 12), 
                                             fg=self.colors['text_gray'], 
                                             bg=self.colors['bg_medium'])
        self.change_labels[crypto].pack(side='right')
        
        # Изменение за 30 дней
        change_30d_frame = tk.Frame(card_frame, bg=self.colors['bg_medium'])
        change_30d_frame.pack(fill='x', padx=10, pady=5)
        
        change_30d_label = tk.Label(change_30d_frame, text="30d:", 
                                   font=('Courier', 10), 
                                   fg=self.colors['text_gray'], 
                                   bg=self.colors['bg_medium'])
        change_30d_label.pack(side='left')
        
        self.change_30d_labels = getattr(self, 'change_30d_labels', {})
        self.change_30d_labels[crypto] = tk.Label(change_30d_frame, text="0.00%", 
                                                 font=('Courier', 12), 
                                                 fg=self.colors['text_gray'], 
                                                 bg=self.colors['bg_medium'])
        self.change_30d_labels[crypto].pack(side='right')
        
        return card_frame
    
    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"TIME: {current_time}")
        self.root.after(1000, self.update_time)
    
    def start_data_fetch(self):
        # Запуск WebSocket для Binance
        threading.Thread(target=self.run_websocket, daemon=True).start()
        
        # Запуск REST API для получения дополнительных данных
        threading.Thread(target=self.fetch_rest_data, daemon=True).start()
        
        # Запуск принудительного обновления каждые 10 секунд
        threading.Thread(target=self.force_update_loop, daemon=True).start()
    
    def run_websocket(self):
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Обработка ping/pong
                if "pong" in data:
                    print("Received pong from Binance")
                    return
                
                if "data" in data and data["stream"].endswith("@miniTicker"):
                    # Проверяем наличие всех необходимых полей
                    if "s" not in data["data"] or "c" not in data["data"]:
                        return
                    
                    symbol = data["data"]["s"].lower()
                    price = float(data["data"]["c"])
                    
                    # Безопасное получение изменения за 24 часа
                    change_24h = 0.0
                    if "P" in data["data"]:
                        try:
                            change_24h = float(data["data"]["P"])
                        except (ValueError, TypeError):
                            change_24h = 0.0
                    
                    # Обновление данных
                    for crypto, info in self.crypto_data.items():
                        if info['symbol'] == symbol:
                            info['price_usd'] = price
                            info['price_rub'] = price * self.usd_rub_rate if self.usd_rub_rate > 0 else 0
                            info['change_24h'] = change_24h
                            self.update_crypto_display(crypto)
                            break
                    
                    self.last_update = datetime.now().strftime("%H:%M:%S")
                    self.status_label.config(text=f"WEBSOCKET | LAST UPDATE: {self.last_update}")
                    self.websocket_connected = True
            except Exception as e:
                print(f"WebSocket message error: {e}")
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
            self.status_label.config(text="CONNECTION ERROR - RECONNECTING...", fg=self.colors['neon_pink'])
            self.websocket_connected = False
            threading.Timer(5, self.run_websocket).start()
        
        def on_close(ws, close_status_code, close_msg):
            print(f"WebSocket connection closed: {close_status_code} - {close_msg}")
            self.status_label.config(text="DISCONNECTED - RECONNECTING...", fg=self.colors['neon_pink'])
            self.websocket_connected = False
            threading.Timer(5, self.run_websocket).start()
        
        def on_open(ws):
            print("WebSocket connected successfully")
            self.status_label.config(text="SUBSCRIBING TO BINANCE STREAMS...", fg=self.colors['neon_green'])
            
            # Подписка на стримы
            subscribe_message = {
                "method": "SUBSCRIBE",
                "params": [f"{info['symbol']}@miniTicker" for info in self.crypto_data.values()],
                "id": 1
            }
            print(f"Sending subscription: {subscribe_message}")
            ws.send(json.dumps(subscribe_message))
            
            # Запуск ping каждые 30 секунд для проверки активности
            def ping_loop():
                while ws.sock and ws.sock.connected:
                    try:
                        time.sleep(30)
                        ws.send(json.dumps({"method": "ping"}))
                    except:
                        break
            
            threading.Thread(target=ping_loop, daemon=True).start()
        
        try:
            ws_url = "wss://stream.binance.com:9443/stream"
            print(f"Connecting to: {ws_url}")
            ws = websocket.WebSocketApp(ws_url, on_open=on_open, on_message=on_message,
                                       on_error=on_error, on_close=on_close)
            ws.run_forever()
        except Exception as e:
            print(f"Failed to create WebSocket connection: {e}")
            self.status_label.config(text="WEBSOCKET CREATION FAILED", fg=self.colors['neon_pink'])
            threading.Timer(5, self.run_websocket).start()
    
    def fetch_rest_data(self):
        """Получение курса USD/RUB и дополнительных данных через REST API"""
        while True:
            try:
                # Получение курса USD/RUB
                response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.usd_rub_rate = data['rates']['RUB']
                    
                    # Обновление цен в рублях
                    for crypto, info in self.crypto_data.items():
                        if info['price_usd'] > 0:
                            info['price_rub'] = info['price_usd'] * self.usd_rub_rate
                            self.update_crypto_display(crypto)
                
                # Если WebSocket не подключен, получаем данные через REST API
                if not self.websocket_connected:
                    self.fetch_crypto_prices_rest()
                
                time.sleep(5)  # Обновление каждые 5 секунд для более частых обновлений
            except Exception as e:
                print(f"REST API error: {e}")
                time.sleep(60)
    
    def fetch_crypto_prices_rest(self):
        """Получение цен криптовалют через REST API Binance"""
        try:
            for crypto, info in self.crypto_data.items():
                symbol = info['symbol'].upper()
                
                # Получение данных за 24 часа
                try:
                    response_24h = requests.get(f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}', timeout=10)
                    if response_24h.status_code == 200:
                        data_24h = response_24h.json()
                        
                        # Безопасное получение данных
                        if 'lastPrice' in data_24h and 'priceChangePercent' in data_24h:
                            price = float(data_24h['lastPrice'])
                            change_24h = float(data_24h['priceChangePercent'])
                            
                            info['price_usd'] = price
                            info['price_rub'] = price * self.usd_rub_rate if self.usd_rub_rate > 0 else 0
                            info['change_24h'] = change_24h
                        else:
                            print(f"Missing required fields in 24h data for {crypto}: {data_24h}")
                    else:
                        print(f"Failed to get 24h data for {crypto}: HTTP {response_24h.status_code}")
                        
                except Exception as e:
                    print(f"Error fetching 24h data for {crypto}: {e}")
                
                # Получение данных за 30 дней (через Kline API)
                try:
                    # Получаем данные за последние 30 дней
                    end_time = int(time.time() * 1000)
                    start_time = end_time - (30 * 24 * 60 * 60 * 1000)  # 30 дней назад
                    
                    response_30d = requests.get(
                        f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&startTime={start_time}&endTime={end_time}&limit=30',
                        timeout=10
                    )
                    
                    if response_30d.status_code == 200:
                        klines_data = response_30d.json()
                        if len(klines_data) >= 2:
                            # Первая и последняя свеча за 30 дней
                            first_price = float(klines_data[0][1])  # Цена открытия первой свечи
                            last_price = float(klines_data[-1][4])  # Цена закрытия последней свечи
                            
                            # Расчет изменения за 30 дней
                            change_30d = ((last_price - first_price) / first_price) * 100
                            info['change_30d'] = change_30d
                        else:
                            info['change_30d'] = 0
                    else:
                        print(f"Failed to get 30d data for {crypto}: {response_30d.status_code}")
                        info['change_30d'] = 0
                        
                except Exception as e:
                    print(f"Error fetching 30d data for {crypto}: {e}")
                    info['change_30d'] = 0
                
                self.update_crypto_display(crypto)
                    
            self.last_update = datetime.now().strftime("%H:%M:%S")
            self.status_label.config(text=f"REST API | LAST UPDATE: {self.last_update}")
        except Exception as e:
            print(f"REST API crypto fetch error: {e}")
    
    def force_update_loop(self):
        """Принудительное обновление данных каждые 10 секунд"""
        while True:
            try:
                time.sleep(10)
                # Если WebSocket не работает, принудительно обновляем через REST API
                if not self.websocket_connected:
                    self.fetch_crypto_prices_rest()
                    self.status_label.config(text=f"FORCED UPDATE | LAST UPDATE: {self.last_update}", fg=self.colors['neon_yellow'])
                else:
                    # Проверяем, что WebSocket действительно работает
                    if time.time() - time.mktime(time.strptime(self.last_update, "%H:%M:%S")) > 30:
                        print("WebSocket seems inactive, forcing REST API update")
                        self.websocket_connected = False
                        self.fetch_crypto_prices_rest()
            except Exception as e:
                print(f"Force update error: {e}")
                time.sleep(5)
    
    def update_crypto_display(self, crypto):
        """Обновление отображения криптовалюты"""
        data = self.crypto_data[crypto]
        
        # Обновление цен
        if crypto in self.usd_price_labels:
            self.usd_price_labels[crypto].config(text=f"${data['price_usd']:,.4f}")
        
        if crypto in self.rub_price_labels:
            self.rub_price_labels[crypto].config(text=f"₽{data['price_rub']:,.2f}")
        
        # Обновление изменения за 24ч
        if crypto in self.change_labels:
            change = data['change_24h']
            color = self.colors['neon_green'] if change >= 0 else self.colors['neon_pink']
            self.change_labels[crypto].config(text=f"{change:+.2f}%", fg=color)
        
        # Обновление изменения за 30 дней
        if crypto in self.change_30d_labels:
            change_30d = data['change_30d']
            color_30d = self.colors['neon_green'] if change_30d >= 0 else self.colors['neon_pink']
            self.change_30d_labels[crypto].config(text=f"{change_30d:+.2f}%", fg=color_30d)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CyberpunkCryptoTracker()
    app.run()