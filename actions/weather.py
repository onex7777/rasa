from typing import Any, Dict, List, Text, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import datetime
import os
import requests
import json
from requests import ConnectionError, HTTPError, TooManyRedirects, Timeout
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
)
# from dotenv import load_dotenv
#
# load_dotenv()
KEY = os.getenv("SENIVERSE_KEY", "")  # API key
API = "https://api.seniverse.com/v3/weather/daily.json"  # API URL
UNIT = "c"  # 温度单位
LANGUAGE = "zh-Hans"  # 查询结果的返回语言
one_day_timedelta = datetime.timedelta(days=1)


def fetch_weather(location: str, start=-3, days=11) -> dict:
    # result = requests.get(
    #     API,
    #     params={
    #         "key": KEY,
    #         "location": location,
    #         "language": LANGUAGE,
    #         "unit": UNIT,
    #         "start": start,
    #         "days": days,
    #     },
    #     timeout=2,
    # )
    today = datetime.datetime.now()
    one_more_day = datetime.timedelta(days=1)
    result = {"results": [{"location": {"id": "1", "name": location}, "daily": [
        {"date": (today + one_more_day * (start + 0)).date(), "text_day": "多云", "text_night": "多云", "high": "26",
         "low": "15"},
        {"date": (today + one_more_day * (start + 1)).date(), "text_day": "晴天", "text_night": "多云", "high": "30",
         "low": "26"},
        {"date": (today + one_more_day * (start + 2)).date(), "text_day": "大晴天", "text_night": "多云", "high": "35",
         "low": "28"},
        {"date": (today + one_more_day * (start + 3)).date(), "text_day": "多云", "text_night": "阴天", "high": "30",
         "low": "26"},
        {"date": (today + one_more_day * (start + 4)).date(), "text_day": "阴天", "text_night": "阴天", "high": "26",
         "low": "25"},
        {"date": (today + one_more_day * (start + 5)).date(), "text_day": "晴天", "text_night": "阴天", "high": "26",
         "low": "22"},
        {"date": (today + one_more_day * (start + 6)).date(), "text_day": "小雨", "text_night": "小雨", "high": "20",
         "low": "15"},
        {"date": (today + one_more_day * (start + 7)).date(), "text_day": "中雨", "text_night": "小雨", "high": "18",
         "low": "10"},
        {"date": (today + one_more_day * (start + 8)).date(), "text_day": "中雨", "text_night": "中雨", "high": "18",
         "low": "12"},
        {"date": (today + one_more_day * (start + 9)).date(), "text_day": "大雨", "text_night": "中雨", "high": "15",
         "low": "12"},
        {"date": (today + one_more_day * (start + 10)).date(), "text_day": "小雨", "text_night": "阴天", "high": "18",
         "low": "15"}]}]
              }
    return result


def get_weather_by_date(location: str, date: datetime.date) -> dict:
    day_timedelta = date - datetime.datetime.today().date()
    day = day_timedelta // one_day_timedelta

    return get_weather_by_day(location, day)


def get_weather_by_day(location: str, day=1) -> dict:
    result = fetch_weather(location)
    print(result)
    normal_result = {
        "location": result["results"][0]["location"],
        "result": result["results"][0]["daily"][day],
    }

    return normal_result


def get_text_weather_date(
        address: str, date_time: datetime.date, raw_date_time: str
) -> str:
    try:
        result = get_weather_by_date(address, date_time)
    except (ConnectionError, HTTPError, TooManyRedirects, Timeout) as e:
        text_message = "{}".format(e)
    else:
        text_message_tpl = "{} {} ({}) 的天气情况为：白天：{}；夜晚：{}；气温：{}-{} 度"
        text_message = text_message_tpl.format(
            result["location"]["name"],
            raw_date_time,
            result["result"]["date"],
            result["result"]["text_day"],
            result["result"]["text_night"],
            result["result"]["high"],
            result["result"]["low"],
        )

    return text_message


def text_to_date(text_date: str) -> Optional[datetime.date]:
    """convert text based Chinese date info into datatime object

    if the convert is not supprted will return None
    """

    today = datetime.datetime.now()
    one_more_day = datetime.timedelta(days=1)

    if text_date == "今天":
        return today.date()
    if text_date == "明天":
        return (today + one_more_day).date()
    if text_date == "后天":
        return (today + one_more_day * 2).date()

    # Not supported by weather API provider freely
    if text_date == "大后天":
        # return 3
        return (today + one_more_day * 3).date()

    if text_date.startswith("星期"):
        # not supported yet
        return None

    if text_date.startswith("下星期"):
        # not supported yet
        return (today + one_more_day * 7).date()

    # follow APIs are not supported by weather API provider freely
    if text_date == "昨天":
        return (today - one_more_day).date()
    if text_date == "前天":
        return (today - one_more_day * 2).date()
    if text_date == "大前天":
        return (today - one_more_day * 3).date()


class ActionWeatherForm(Action):
    def name(self) -> Text:
        return "action_weather_form_submit"

    def run(
            self, dispatch: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict]:
        city = tracker.get_slot("address")
        date_text = tracker.get_slot("date-time")

        date_object = text_to_date(date_text)

        if not date_object:  # parse date_time failed
            msg = "暂不支持查询 {} 的天气".format([city, date_text])
            dispatch.utter_message(msg)
        else:
            try:
                weather_data = get_text_weather_date(
                    city, date_object, date_text)
            except Exception as e:
                exec_msg = str(e)
                dispatch.utter_message(exec_msg)
            else:
                dispatch.utter_message(weather_data)

        return [SlotSet("address", None),
                SlotSet("date-time", None)]
