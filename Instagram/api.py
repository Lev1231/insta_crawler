# -*- coding: utf-8 -*-

import json
# from urllib.request import urlopen
import requests

import detectlanguage

from Instagram import config


def languageDetection(text):
    detectlanguage.configuration.api_key = config.detectlanguageApi_key
    try:
        re = detectlanguage.simple_detect(text)
    except:
        re = 'unknown'

    return re

def genderDetectionByName(name):
    myKey = config.genderApi_key
    url = "https://gender-api.com/get?key=" + myKey + "&name=%s"%name

    # response = urlopen(url)
    # decoded = response.read().decode('utf-8')
    # data = json.loads(decoded)

    r = requests.get(url)
    data = r.json()

    return data["gender"]


if __name__ == "__main__":
    # text = "渡辺直美"
    # print (languageDetection(text))

    genderDetectionByName('S I R  J O H N'.encode('utf-8'))
