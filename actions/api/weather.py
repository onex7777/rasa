

import requests


def weather_api(city):
    url = 'https://tianqiapi.com/api?unescape=1&version=v1&appid=37888876&appsecret=cRwpG1rw'
    params = {}
    params['city'] = city
    r = requests.request("GET", url, params=params)
    if r.status_code != 200:
        return []
    else:
        x = r.content
        data = eval(x)
        return data['data']



