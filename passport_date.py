import time
import json
import datetime
import requests
from telegram import Bot

# if you want message sent to telegram
TOKEN = 'TELEGRAM TOKEN'
CHAT_ID = 'Telegram chat ID'
bot = Bot(token=TOKEN)
session = requests.Session()
valid_dates = []
earliest_valid_date = None
earliest_valid_time = None

def get_valid_dates():
  # see the url for your location from inspect element, for morang it is 33.
  response = session.get("https://emrtds.nepalpassport.gov.np/iups-api/calendars/33/false")
  data = json.loads(response.content)
  min_date = datetime.datetime.strptime(data['minDate'], "%Y-%m-%d")
  max_date = datetime.datetime.strptime(data['maxDate'], "%Y-%m-%d")
  off_dates = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in data['offDates']]
  current_date = min_date
  while current_date <= max_date:
    if current_date not in off_dates:
      valid_dates.append(current_date.strftime("%Y-%m-%d"))
    current_date += datetime.timedelta(days=1)

counter = 0

while True:
  get_valid_dates()
  for valid_date in valid_dates:
    url = f"https://emrtds.nepalpassport.gov.np/iups-api/timeslots/33/{valid_date}/false"
    response = session.get(url)
    data = json.loads(response.content)
    for time_slot in data:
      if time_slot["status"] and time_slot["capacity"] > 0:
        earliest_valid_date = valid_date
        earliest_valid_time = time_slot["name"]
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"date found: {current_time} The earliest valid date and time is: {earliest_valid_date} {earliest_valid_time}")
        bot.send_message(chat_id=CHAT_ID, text=f'The earliest valid date and time is: {earliest_valid_date} {earliest_valid_time}')
        break
    if earliest_valid_time:
      break
  counter += 1
  print(" loop counter: {}\r".format(counter), end=" ")
  time.sleep(5)
