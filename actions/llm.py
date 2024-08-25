# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Dict, List, Text, Optional
import datetime
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests


Qwen_URL = 'http://127.0.0.1:8002'
headers = {"Content-Type": "application/json"}
one_day_timedelta = datetime.timedelta(days=1)
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



class ActionLocalLlm(Action):
    def name(self) -> Text:
        return "action_local_llm"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取最近的信息
        text_of_last_user_message = tracker.latest_message.get("text")
        prompt = """假如您是一位智能助手，请结合你自身的知识对客户的问题进行回答和推荐:
        客户: ”{}“
        要求：
        1、使用100个字内进行回答；
        2、不得捏造事实，如果无法回答问题，请回复："我不明白您的意思，可以说清楚一遍嘛？""".format(text_of_last_user_message)
        try:
            response = requests.post(Qwen_URL, headers=headers, json=prompt)
            if response.status_code == 200:
                answer = response.text
                dispatcher.utter_message(text=answer)
                return []
            else:
                print(f"Error: {response.status_code}")
                return []
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return []

