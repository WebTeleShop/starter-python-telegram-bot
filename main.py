import telebot
from telebot import types
import requests
import time
import segno
import telegram

SessionID = 0

bot = telebot.TeleBot('6489402081:AAHrE1LAWOIWJnTWZRntkQtzXlBATNMgxY0')

# GET COOKIES
def getcookie():
    try:
        with open('cookieShopee.txt', 'r') as file:
            cookie = file.read()
            
            if not cookie:
                # print("\nFILE COOKIES KOSONG, GUNAKAN FITUR 1 DAHULU.")
                time.sleep(5)
                return None
            return cookie
    
    except FileNotFoundError:
        # print("\nFILE COOKIES TIDAK DITEMUKAN, GUNAKAN FITUR 1 DAHULU.")
        time.sleep(5)

cookie = getcookie()
cookies = {'SPC_EC': f'{cookie}',} 

headers = {
        "authority": "shopee.co.id",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        "client-info": "platform=9",
        'X-Shopee-Language': 'id',
        'X-Requested-With': 'XMLHttpRequest',
        }

headers_live = {
        "authority": "live.shopee.co.id",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        "client-info": "platform=9",
        'X-Shopee-Language': 'id',
        'X-Requested-With': 'XMLHttpRequest',
        }

@bot.message_handler(commands=['start'])
def greet(message):
    keyboard = types.InlineKeyboardMarkup()
    login = types.InlineKeyboardButton(text="Login", callback_data="/login")
    GetInfo = types.InlineKeyboardButton(text="Get Data", callback_data="/info")
    GetRtmp = types.InlineKeyboardButton(text="Get RTMP", callback_data="/rtmp")
    Help = types.InlineKeyboardButton(text="Info Bantuan!", callback_data="/help")
    keyboard.add(login, GetInfo, GetRtmp, Help)
    bot.send_message(message.chat.id, "Hello, Gaes!\nWelcome to <b>RTMP Shopee Live Bot</b>\n\nSilahkan Pilih Menu :", reply_markup=keyboard, parse_mode=telegram.constants.ParseMode.HTML)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "/info":
            getInfoAccount(call.message)
        if call.data == "/rtmp":
            GetRTMP(call.message)
        if call.data == "/login":
            getLogin(call.message)
        if call.data == "/help":    
            helpinfo(call.message)

@bot.message_handler(func=lambda message: True)
def getHome(message):
    bot.send_message(message.chat.id, 
                     """Menu Tidak Ditemukan!\n
    /start - Menu Utama!
    
                     """, parse_mode=telegram.constants.ParseMode.HTML)
    
# LOGIN
# @bot.message_handler(commands=['login'])
@bot.message_handler(func=lambda message: True)
def getLogin(message):
    qrcode_id = getQrLogin(message)
    while True:
        checkQrStatus(qrcode_id, message)
        time.sleep(1)
        
def getQrLogin(message):
    qrLogin = requests.get('https://shopee.co.id/api/v2/authentication/gen_qrcode', headers=headers)
    if qrLogin.status_code == 200:
        result = qrLogin.json()
        qrcode_id = result["data"]["qrcode_id"]
        if qrcode_id:
            qrcode = segno.make_qr(f"https://shopee.co.id/universal-link/qrcode-login?id={qrcode_id}")
            
            # CREATE QR LOGIN
            qrcode.save("login_qrcode.png", scale=5,)
            viewQrcode = open('login_qrcode.png', 'rb')
            bot.send_photo(message.chat.id, viewQrcode)
            return qrcode_id
        else:
            Qrcode = "[!] Failed get new QR."
            bot.send_message(message.chat.id, Qrcode, parse_mode=telegram.constants.ParseMode.HTML)
    else:
        Qrcode = "[!] Failed create QR login."
        bot.send_message(message.chat.id, Qrcode, parse_mode=telegram.constants.ParseMode.HTML)

def checkQrStatus(qrcode_id, message):
    cookies = {
    '__LOCALE__null': 'ID',
    }
    params = {
        "qrcode_id": qrcode_id,
    }
    response = requests.get(
        "https://shopee.co.id/api/v2/authentication/qrcode_status",
        params=params,
        cookies=cookies,
        headers=headers,
    )
    if response.status_code == 200:
        result = response.json()
        statusQR = result["data"]["status"]
        if statusQR == 'NEW':
            Qrcode = f"[{statusQR}] <b>SCAN QRCODE</b> WITH YOUR APP | Delay 90 seconds.."
            bot.send_message(message.chat.id, Qrcode, parse_mode=telegram.constants.ParseMode.HTML)
            time.sleep(90)
        elif statusQR == 'SCANNED':
            Qrcode = "                                       "
            Qrcode = f"[{statusQR}] CONFIRM IN YOUR APP! "
            bot.send_message(message.chat.id, Qrcode, parse_mode=telegram.constants.ParseMode.HTML)
        elif statusQR == 'CONFIRMED':
            Qrcode = "                              "
            tokenQR = result["data"]["qrcode_token"]
            getCookiesLogin(tokenQR, message)
            exit()
        elif statusQR == 'EXPIRED':
            Qrcode = "                                        "
            Qrcode = f"QR {statusQR}!\n"
            bot.send_message(message.chat.id, Qrcode, parse_mode=telegram.constants.ParseMode.HTML)
            exit()
        else:
            Qrcode = "                              "
            Qrcode = statusQR
            bot.send_message(message.chat.id, Qrcode, parse_mode=telegram.constants.ParseMode.HTML)
    else:
        Qrcode = "[!] Failed checking status QR"
        bot.send_message(message.chat.id, Qrcode, parse_mode=telegram.constants.ParseMode.HTML)
        exit()

def getCookiesLogin(tokenQR, message):
    postData = {
        "qrcode_token": tokenQR,
        "device_sz_fingerprint": "OazXiPqlUgm158nr1h09yA==|0/eMoV7m/rlUHbgxsRgRC/n0vyOe6XzhDMa2PcnZPv3ecioRaJQg2W7ur5GfhoDDEeuMz2az7GGj/8Y=|Pu2hbrwoH+45rDNC|08|3",
        "client_identifier": {
            "security_device_fingerprint": "OazXiPqlUgm158nr1h09yA==|0/eMoV7m/rlUHbgxsRgRC/n0vyOe6XzhDMa2PcnZPv3ecioRaJQg2W7ur5GfhoDDEeuMz2az7GGj/8Y=|Pu2hbrwoH+45rDNC|08|3",
        },
    }
    url = "https://shopee.co.id/api/v2/authentication/qrcode_login"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    login_response = requests.post(url, json=postData, headers=headers)
    result = login_response.headers.get('Set-Cookie', '').split(', ')
    
    all_cookies = {}
    
    for cookie_value in result:
        cookie_parts = cookie_value.split('; ')
        if cookie_parts:
            cookie_name, cookie_data = cookie_parts[0].split('=', 1)
            all_cookies[cookie_name] = cookie_data

    # spc_ec_cookie = all_cookies.get('SPC_EC', '')
    spc_st_cookie = all_cookies.get('SPC_ST', '')
    with open('cookieShopee.txt', 'w') as file:
        file.write(spc_st_cookie)
        Qrcode = "<b>CONFIRMED!</b> SUCCESS SAVED COOKIE ACCOUNT.\n"
        bot.send_message(message.chat.id, Qrcode, parse_mode=telegram.constants.ParseMode.HTML)
        getInfoAccount(message)

    
# @bot.message_handler(commands=['rtmp'])
@bot.message_handler(func=lambda message: True)
def GetRTMP(message):
    sent = bot.send_message(message.chat.id, '<b>Session ID Live Example :</b>\n xxx.shopee.co.id/insight/live/5885xxxx\nInput Sesi (5885xxxx) : ', parse_mode=telegram.constants.ParseMode.HTML)
    bot.register_next_step_handler(sent, getRTMPAccount)        

def getRTMPAccount(message):
    headers = {
        'authority': "live.shopee.co.id",
        'method': "GET",
        'user-agent': "okhttp/3.12.4 app_type=1",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'content-type': "application/json;charset=UTF-8"
    }
     
    response = requests.get(
    f'https://live.shopee.co.id/api/v1/session/{message.text}/push_url_list?ver=2',
    headers=headers,
    cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        try:
            for i in data['data']['push_addr_list']:
                Rurl = i['push_url']
                xRurl = Rurl.split("id-")
                rtmpData = f"========[ <b> Shopee RTMP Live </b> ]======== \n \n ▶️ <b>URL Server</b> :\n <code>{xRurl[0]}</code> \n \n ▶️ <b>Streaming Key</b> :\n <code>id-{xRurl[1]}</code>"
                bot.send_message(message.chat.id, rtmpData, parse_mode=telegram.constants.ParseMode.HTML)
        except:
            bot.send_message(message.chat.id, 'Session ID Tidak Ditemukan!', parse_mode=telegram.constants.ParseMode.HTML)
    else:
        bot.send_message(message.chat.id, 'Account Shopee Not Connected!', parse_mode=telegram.constants.ParseMode.HTML)


# @bot.message_handler(commands=['info'])
@bot.message_handler(func=lambda message: True)
def getInfoAccount(message):
    response = requests.get(
    f'https://shopee.co.id/api/v4/account/basic/get_account_info',
    headers=headers,
    cookies=cookies,
    )
    
    if response.status_code == 200:
        data = response.json() 
        teldata = f"====== <b> Details Account </b> ====== \n Username : {data['data']['username']} \n Email : {data['data']['email']} \n Nama Toko : {data['data']['nickname']}"
        # print(teldata)
        bot.send_message(message.chat.id, teldata, parse_mode=telegram.constants.ParseMode.HTML)  
    else:
        bot.send_message(message.chat.id, 'Account Shopee Not Connected!', parse_mode=telegram.constants.ParseMode.HTML) 

# @bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: True)
def helpinfo(message):
    bot.send_message(message.chat.id, "Hello! Im <b>RTMP Shopee Live Bot</b> Thanks For Support.", parse_mode=telegram.constants.ParseMode.HTML)

bot.polling()
