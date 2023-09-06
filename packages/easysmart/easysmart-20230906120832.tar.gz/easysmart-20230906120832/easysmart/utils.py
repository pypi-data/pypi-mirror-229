import json
import os
import pathlib
import time

import requests
import zipfile
from pathlib import Path
import sys
from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG

def on_log(client, userdata, level, buf):
    if level == MQTT_LOG_INFO:
        head = 'INFO'
    elif level == MQTT_LOG_NOTICE:
        head = 'NOTICE'
    elif level == MQTT_LOG_WARNING:
        head = 'WARN'
    elif level == MQTT_LOG_ERR:
        head = 'ERR'
    elif level == MQTT_LOG_DEBUG:
        head = 'DEBUG'
    else:
        head = level
    print('%s: %s' % (head, buf))


def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    # client.subscribe(topic, 0)


def on_message(client, userdata, msg):
    print('topic:' + msg.topic + ' ' + str(msg.payload))
    try:
        data = json.loads(msg.payload)
    except:
        data = str(msg.payload)
    print(f'{data}')


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected disconnection %s' % rc)


def start_emqx_server(path=None):
    print(f'system is {sys.platform}')
    if sys.platform == 'win32':
        pass
    else:
        raise NotImplementedError('only support windows now')
    if path is None:
        path = homedir = str(pathlib.Path.home())
    # check emqx server
    if check_emqx_server(path):
        return
    print(f'starting emqx server at {path}')
    # if path not exists, create it
    if not os.path.exists(path):
        os.makedirs(path)
    p = Path(path)
    emqx_path = p / r'emqx\bin\emqx'
    # 检测emqx是否存在
    if not os.path.exists(emqx_path):
        download_emqx(path)
    # start emqx by run "emqx\bin\emqx start"
    os.system(f"{emqx_path} start")
    print('emqx server started')


def check_emqx_server(path=None):
    print(f'check emqx server at {path}')
    # if path not exists, create it
    if not os.path.exists(path):
        os.makedirs(path)
    p = Path(path)
    emqx_path = p / r'emqx\bin\emqx_ctl'
    # 检测emqx是否正在运行
    # run "emqx\bin\emqx status" and get the result
    result = os.popen(f"{emqx_path} status").read()
    print(f'emqx status is {result}')
    if 'is started' in result:
        print('emqx server is running')
        return True
    else:
        print('emqx server is not running')
        return False


def download_emqx(path):
    print('emqx not found, downloading...')
    download_url = r'https://www.emqx.com/zh/downloads/broker/5.0.26/emqx-5.0.26-windows-amd64.zip'
    r = requests.get(download_url)
    p = Path(path)
    zip_path = p / r'emqx.zip'
    with open(zip_path, 'wb') as f:
        f.write(r.content)
    print('download finished ,unziping...')
    time.sleep(1)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path=p / 'emqx')
    print('unzip finished')
    time.sleep(1)


if __name__ == '__main__':
    start_emqx_server()
    # check_emqx_server()
