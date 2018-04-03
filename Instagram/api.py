import json
import requests
from urllib.request import urlopen

import detectlanguage
from googletrans import Translator

from Instagram import config

def transalte(text):
    translator = Translator()
    translation = translator.translate(text)

    return translation.text

def languageDetection(text):
    # print (text)
    detectlanguage.configuration.api_key = config.detectlanguageApi_key
    try:
        re = detectlanguage.detect(text)
        all_confidence = sum([item.get('confidence') for item in re])
        re = ', '.join([item.get('language')+":"+str(round(item.get('confidence')/all_confidence*100, 2))+"%"  for item in re])
    except Exception as e:
        print (e)
        re = 'unknown'

    return re

def genderDetectionByName(name):
    # print (name)
    eng_name = transalte(name)
    myKey = config.genderApi_key
    url = "https://gender-api.com/get?key=" + myKey + "&name=%s"%eng_name

    r = requests.get(url)
    data = r.json()

    return data["gender"]


if __name__ == "__main__":
    # text = "渡辺直美 you are good 渡辺直美"
    # print (languageDetection(text))

    # genderDetectionByName('S I R  J O H N'.encode('utf-8'))
    print (genderDetectionByName('香取慎吾'))