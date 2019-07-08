#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config
import subprocess
import datetime
from PIL import Image
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from requests_oauthlib import OAuth1Session
import json

strLog = ''


# ログに文字列を追加。同時に標準出力にも出力
def setLog(str):
    global strLog
    strLog += str
    print(str)

# ログ文字列を取得
def getLog():
    global strLog
    return strLog

# ログ文字列をクリア
def clrLog():
    global strLog
    strLog = ''


# 写真を撮る。
def shutter(fName):
    cmd = [
        'raspistill',
        '--nopreview',
        '--drc', 'low',
        #'--saturation', '15',
        '--output', fName,
        '--verbose',
        ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE)
    setLog(proc.stdout.decode('utf8'))

#ret = subprocess.call(cmd)

#   if ret == 0:
#       print("Image is saved as {}".format(fName))
#   else:
#       print("Image is not saved")

#   return ret


# 画像を縮小
def shrinkImage(fName, fNameS):
    img = Image.open(fName)
    w, h = img.size
    h_new = 1080
    w_new = (int)(w * h_new / h)
    img = img.resize((w_new, h_new))
    img.save(fNameS)

    setLog("Image is shrinked to w={}, h={}\n".format(w_new, h_new))


# 引数の画像ファイルを添付してTweet
def tweet(fName):
    URL_MEDIA = 'https://upload.twitter.com/1.1/media/upload.json'
    URL_STATUS = 'https://api.twitter.com/1.1/statuses/update.json'

    twitter = OAuth1Session(config.TW_CONSUMER_API_KEY, config.TW_CONSUMER_API_SEC, config.TW_ACCESS_TOKEN, config.TW_ACCESS_TOKEN_SEC)

    with open(fName, 'rb') as f:
        data = f.read()
        files = {"media" : data}
        res = twitter.post(URL_MEDIA, files=files)
        print('media upload response = {}'.format(res.status_code))

    if res.status_code == 200:
        media_id = json.loads(res.text)['media_id']
        strDate = datetime.datetime.now().strftime('%Y,%m,%d %H:%M')
        status = '毎日自動で撮影中。 #今日の庭 #ラズパイカメラ #定点観測 \n' + strDate
        params = {
            'status' : status,
            'media_ids' : [media_id]
        }
        res = twitter.post(URL_STATUS, params=params)
        print('status update response = {}'.format(res.status_code))


# 縮小した画像をメールで送信
def sendMail(fName):
    # メッセージ作成
    msg = MIMEMultipart()
    msg['Subject'] = '[niwalaps] ' + os.path.basename(fName)
    msg['From'] = config.GM_ADDR
    msg['To'] = config.GM_ADDR
    msg.attach(MIMEText(getLog()))

    # 画像を添付
    with open(fName, 'rb') as fp:
        img = MIMEImage(fp.read())
    msg.attach(img)

    # 送信
    print('sendmail:1')
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    print('sendmail:2')
    smtp.starttls()
    print('sendmail:3')
    smtp.login(config.GM_ADDR, config.GM_PASS)
    print('sendmail:4')
    smtp.send_message(msg)
    print('sendmail:5')
    smtp.quit()
    print('sendmail:6')


def main():
    clrLog()

    # 現在時刻からファイル名を決定
    strDate = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    fName = '/home/pi/data/waniwa/img/waniwa_{}.jpg'.format(strDate)
    fNameS = '/home/pi/data/waniwa/simg/waniwa_{}.jpg'.format(strDate)

    shutter(fName)
    shrinkImage(fName, fNameS)
    sendMail(fNameS)
    #tweet(fNameS)

if __name__ == "__main__":
    main()
