# -*- coding: utf-8 -*-

import json
from urllib.request import urlopen

import detectlanguage

import config


def languageDetection(text):
    detectlanguage.configuration.api_key = config.detectlanguageApi_key
    re = detectlanguage.simple_detect(text)

    return re

def genderDetectionByName(name):
    myKey = config.genderApi_key
    url = "https://gender-api.com/get?key=" + myKey + "&name=%s"%name
    response = urlopen(url)
    decoded = response.read().decode('utf-8')
    data = json.loads(decoded)

    return data["gender"]

if __name__ == "__main__":
    text = "渡辺直美"
    print (languageDetection(text))


