import json, time, argparse
import datetime

from influxdb_client import InfluxDBClient, Point
import redis

#------------------------------#Вот это надо заполнить!------------------------------#
token = ""
org = ""


client = InfluxDBClient(url="http://influxdb:8086", token=token, org=org)
#Убери потом эту хуйню! Засунь эту срань в докер-компост! А то работать не будет!
query_api = client.query_api()



def get_data(bucket:str, board:str, start_date:str, stop_date:str, period:str):
  #2023-12-01T00:00:00Z формат для даты
  query = """from(bucket: "{bucket}")
    |> range(start: {start_date}, stop: {stop_date})
    |> filter(fn: (r) => r["_measurement"] == "Thread")
    |> filter(fn: (r) => r["board"] == "{board}")
    |> filter(fn: (r) => r["_field"] == "text_len")
    |> keep(columns: ["_time", "_field", "_value", "board"])
    |> aggregateWindow(every: {period}, fn: count, createEmpty: true, timeSrc: "_start")
    |> yield(name: "count_per_period")
""".format(bucket = bucket, period = period, board = board, start_date = start_date, stop_date = stop_date)
  influx_result = query_api.query(org=org, query=query)
  #print(influx_result)
  return influx_result


def format_data(influx_result, period:str) -> str:
  #В этой функции используется локальная таймзона
  #Она задается в докер-компосте
  res_not_json_yet = {
        "xValues":[],
        "yValues":[]
    }

  for table in influx_result:
    for record in table.records:
      date_point = record.get_time()
      if period == '1d': #Нужно чтобы сформировать правильный вид даты для удобства отображения
        res_not_json_yet["xValues"].append(date_point.astimezone().strftime('%d-%m-%y'))
      elif period == '1h':
        res_not_json_yet["xValues"].append(date_point.astimezone().strftime('%H:00 %d-%m'))
      else:
        res_not_json_yet["xValues"].append(date_point.astimezone().isoformat())
      res_not_json_yet["yValues"].append(record.get_value())

  json_result = json.dumps(res_not_json_yet)
  print(json_result)
  return json_result


def save_to_cache(json_result:str, json_name:str)->None:
  r = redis.Redis(host="redis", port=6379, decode_responses=True)
  res = r.set(json_name, json_result)
  if res:
    pass
  else:
    print("Could not set data in redis")
  return


def define_range(range):
  curr_time = datetime.datetime.utcnow()
  if range == "month":
    stop_date = datetime.datetime(year=curr_time.year,month=curr_time.month,day=curr_time.day)
    start_date = stop_date - datetime.timedelta(days=30)
  elif range == "3d" or range == "1d":
    stop_date = datetime.datetime(year=curr_time.year,month=curr_time.month,day=curr_time.day, hour=curr_time.hour)
    if range == "3d":
      start_date = stop_date - datetime.timedelta(days=3)
    elif range == "1d":
      start_date = stop_date - datetime.timedelta(days=1)
  else:
    print("Неверный range передан")
  return (start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), stop_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
  

if __name__=='__main__':
  #Для запуска нужны параметры. 
  #bucket - имя борды и он же bucket в инфлюксе, откуда брать
  #board - название доски, как в инфлюксе
  #period - частота дискретизации данных - час, день, как в инфлюксе. 1h, 1d, etc
  #range - константа из функции define_range здесь, month (будет 30 дней), 3d или 1d
  parser = argparse.ArgumentParser()
  parser.add_argument('--bucket', help='Enter bucket name', required=True, type=str)
  parser.add_argument('--board', help='Enter board name', required=True, type=str)
  parser.add_argument('--period', help='Enter period: 1h or 1d', required=True, type=str)
  parser.add_argument('--range', help='Enter range: month, 3d or 1d', required=True, type=str)

  args = parser.parse_args()
  bucket = args.bucket
  board = args.board
  period = args.period
  range = args.range

  start_time = time.time()
  print("Compressing", range, "data for", bucket, "...")

  start_date, stop_date = define_range(range)
  print("Берем промежуток с", start_date, "UTC до", stop_date, "UTC")
  json_name = bucket + "_" + board + "_" + period + "_" + range
  influx_result = get_data(bucket, board, start_date, stop_date, period)
  json_result = format_data(influx_result, period)
  save_to_cache(json_result, json_name)

  run_time = time.time() - start_time
  print("Data compression completed successfully in", run_time)
