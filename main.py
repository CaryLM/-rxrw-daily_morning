from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

# 获取当前日期为星期几
def get_week_day():
  week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
  week_day = week_list[datetime.date(today).weekday()]
  return week_day

def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['temp'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def format_temperature(temperature):
  return math.floor(temperature)

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

weather = get_weather()
if weather is None:
  print('获取天气失败')
  exit(422)
wm = WeChatMessage(client)
wea, temperature = get_weather()
data = {
  "weather":{
    "value":wea
  },
  "temperature":{
    "value":temperature
  },
  "love_days":{
    "value":get_count()
  },
  "birthday_left":{
    "value":get_birthday()
  },
  # 今天周几
  "week_day": {
    "value": get_week_day(),
    "color": get_random_color()
  },
   # 风力
  "wind": {
    "value": weather['wind'],
    "color": get_random_color()
  },
  # 空气质量
  "air_quality": {
    "value": weather['airQuality'],
    "color": get_random_color()
  },
  "words":{
    "value":get_words(), 
    "color":get_random_color()
  }
}
res = wm.send_template(user_id, template_id, data)
print(res)
