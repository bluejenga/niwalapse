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

strLog = ''


# ログに文字列を追加。同時に標準出力にも出力
def setLog(s):
    global strLog
    strLog = strLog + s
    print(s)

# ログ文字列を取得
def getLog():
    global strLog
    return strLog


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

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    setLog(proc.stdout.decode('utf8'))


# 画像を縮小
def shrinkImage(fName, fNameS):
    img = Image.open(fName)
    w, h = img.size
    h_new = 1080
    w_new = (int)(w * h_new / h)
    img = img.resize((w_new, h_new))
    img.save(fNameS)

    setLog("Image is shrinked to w={}, h={}\n".format(w_new, h_new))


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
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(config.GM_ADDR, config.GM_PASS)
    smtp.send_message(msg)
    smtp.quit()


if __name__ == "__main__":

    # 現在時刻からファイル名を決定
    strDate = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    dirName = os.path.dirname(__file__)
    fName = os.path.join(dirName, f'img/waniwa_{strDate}.jpg')
    fNameS = os.path.join(dirName, f'simg/waniwa_{strDate}.jpg')

    shutter(fName)
    shrinkImage(fName, fNameS)
    sendMail(fNameS)

