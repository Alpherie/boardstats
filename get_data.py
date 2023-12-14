import datetime
import uuid
import time
import argparse
import re

import requests as r 
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


#------------------------------#Вот это надо заполнить!------------------------------#
token = ""
org = ""
bucket = "2ch_hk"




client = InfluxDBClient(url="http://influxdb:8086", token=token, org=org)
#Убери потом эту хуйню! Засунь эту срань в докер-компост! А то работать не будет!
write_api = client.write_api(write_options=SYNCHRONOUS)

class SwineCheck(object):
    def __init__(self, board):
        self.influx_points = []
        self.board = board
        self.swine_regexp = re.compile(r'(хо+хо*л)|(тараб?с)|(пидораш(ко|енк))|(у(с+|к)раб?ин)|(протоукр)|(мивин)|(гриве?н)|(киберсв(ы|и)н)|(свино(сот|дво|рез))|(свиня)|(свидом)|(хр+ю+у*)|(зрад)|(перемо(г|ж))|(генотьб)|(майдау?н)|(скак(о|е)л)|(поскачи)|(ципсо)|(рагул)|(безвизг)|(пидарешт)|(мои(|х|ми+|)\s*искандер)|(дупабол)|(м[иыіi]кол)|(б[иа]ндер)|(оксан)|(сало(\w))|(потужн)|(нато\s*допомо(ж|г))')
    def check_str_for_swines(self, string):
        matches = self.swine_regexp.findall(string)
        return len(matches)
    def check_for_swine(self, post):
        comment_prepared = post['comment'].lower()

        count = self.check_str_for_swines(comment_prepared)

        if count > 0:
            #print(count)
            p = Point("Swines")
            p.time(datetime.datetime.utcfromtimestamp(post['timestamp']))
            p.tag("id", post['num'])
            p.tag("board", self.board)
            p.field("num", count)
            self.influx_points.append(p)
    def load_to_influx(self):
        if len(self.influx_points) > 0:
            write_api.write(bucket=bucket, record=self.influx_points)


def get_thread_stats(board):
    res = r.get("https://2ch.hk/"+board+"/catalog_num.json", timeout=20)
    print(res.status_code)
    json = res.json()
    point_list = []
    for t in json['threads']:
        p = Point("Thread")
        p.time(datetime.datetime.utcfromtimestamp(t['timestamp']))
        p.tag("id", t['num'])
        p.tag("board", board)
        p.field("files", len(t['files']))
        p.field("posts_in", t['posts_count'])
        p.field("parent", '-1')
        point_list.append(p)
    write_api.write(bucket=bucket, record=point_list)
    return json['threads']

def get_post_stats(thread_list, board):
    success = 0
    for t in thread_list:
        try:
            res = r.get('https://2ch.hk/'+board+'/res/'+str(t['num'])+'.json', timeout=20)
            if res.status_code == 200:
                success += 1
            json = res.json()
            point_list = []
            swinechecker = SwineCheck(board)
            for post in json['threads'][0]['posts']:
                p = Point("Thread")
                p.time(datetime.datetime.utcfromtimestamp(post['timestamp']))
                p.tag("id", post['num'])
                p.tag("board", board)
                if post['files'] is None:
                    p.field("files", 0)
                else:
                    p.field("files", len(post['files']))
                if post['parent'] != '0' and post['parent'] != 0:
                    p.field("posts_in", -1)
                p.field("parent", str(post['parent']))
                p.field("text_len", len(post['comment']))
                point_list.append(p)
                swinechecker.check_for_swine(post)
            write_api.write(bucket=bucket, record=point_list)
            swinechecker.load_to_influx()
        except Exception as e:
            print(e)
    return (success / len(thread_list))* 100

def get_stats(board):
    print('Запускаю получение статистики')
    print('Запрос списка тредов')
    thread_list = get_thread_stats(board)
    print('Список тредов успешно получен')
    print('Запросы по тредам')
    result_percent = get_post_stats(thread_list, board)
    print('Данные по постам получены, процент успеха:', result_percent)
    return result_percent



if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', help='Enter board name', required=True, type=str)
    args = parser.parse_args()
    board = args.board

    error = "0"
    start_time = time.time()
    run_uuid = uuid.uuid1()
    
    try:
        result_percent = get_stats(board)
        if result_percent != 100.0:
            error = str(result_percent)
    except Exception as e:
        error = "-1"

    run_time = time.time() - start_time
    p = Point("Requesting")
    p.time(datetime.datetime.utcnow())
    p.tag("uuid", run_uuid)
    p.tag("board", board)
    p.field("error", error)
    p.field("req_time", run_time)
    write_api.write(bucket=bucket, record=p)
