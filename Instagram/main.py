import os
import sys
import logging
import codecs
import json
import shutil
import urllib
from time import sleep
import re

# import requests
# from pymongo import MongoClient, ASCENDING

from config import *

# def save_image(username, image_uri):
#     with open(os.path.join(os.path.dirname(__file__), "characters", username+".jpg"), "wb") as f:
#         r = requests.get(image_uri, stream=True)
#         r.raise_for_status()
#         shutil.copyfileobj(r.raw, f)
#
#     return

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')

def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object

def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))

def getAttribute(obj):
    output = {}
    for key, value in obj.__dict__.items():
        if type(value) is list:
            output[key] = [getAttribute(item) for item in value]
        else:
            try:
                output[key] = getAttribute(value)
            except:
                output[key] = value

    return output

class Instagram_DataService():
    '''Main class of the project'''
    def __init__(self, username, password):
        '''
        :param username: Instagram Login Username
        :param password: Instagram Login Password
        '''
        device_id = None
        try:
            settings_file = settings_file_path
            if not os.path.isfile(settings_file):
                # settings file does not exist
                print('Unable to find file: {0!s}'.format(settings_file_path))

                # login new
                self.client = Client(
                    username, password,
                    on_login=lambda x: onlogin_callback(x, settings_file_path))
            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=from_json)
                print('Reusing settings: {0!s}'.format(settings_file))

                device_id = cached_settings.get('device_id')
                # reuse auth settings
                self.client = Client(
                    username, password,
                    settings=cached_settings)

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

            # Login expired
            # Do relogin but use default ua, keys and such
            self.client = Client(
                username, password,
                device_id=device_id,
                on_login=lambda x: onlogin_callback(x, settings_file_path))

        except ClientLoginError as e:
            print('ClientLoginError {0!s}'.format(e))
            exit(9)
        except ClientError as e:
            print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            exit(9)
        except Exception as e:
            print('Unexpected Exception: {0!s}'.format(e))
            exit(99)

        self.user_id = self.client.username_info(username)['user']['pk']

        # client = MongoClient(host, port)
        # self.db = client.instagram

    def last_photos(self, user_id):
        '''
        :param user_id: pk of user in instagram
        '''

        max_id = 0

        post_response = self.client.user_feed(user_id, max_id=max_id)
        last_photos = []
        for post in post_response['items']:
            photo = {}
            try:
                photo['url'] = post['image_versions2']['candidates'][0]['url']
            except KeyError:
                continue
            try:
                photo['likes'] = post['like_count']
            except KeyError:
                photo['likes'] = 0

            try:
                photo['comments'] = post['comment_count']
            except KeyError:
                photo['comments'] = 0

            last_photos.append(photo)
            if len(last_photos) == 6:
                break

        return last_photos


    def get_profile_over50k(self, username):
        user_info = self.client.username_info(username)

        if user_info['user']['follower_count'] >= 5000:
            profile = {}
            profile['id'] = user_info['user']['pk']
            profile['username'] = user_info['user']['username']
            profile['name'] = user_info['user']['full_name']
            profile['followers'] = user_info['user']['follower_count']
            profile['followings'] = user_info['user']['following_count']
            profile['posts'] = user_info['user']['media_count']
            try:
                profile['bio'] = user_info['user']['biography']
            except:
                profile['bio'] = ""
            try:
                profile['email'] = email_regex.search(profile['bio']).group(0)
            except:
                profile['email'] = ""
            try:
                profile['last_photos'] = self.last_photos(profile['id'])
            except ClientError:
                profile['last_photos'] = {}

            # print (profile['username'])
            # print (profile['bio'])
            # print (profile['email'])

            # save_image(profile['username'], user_info['user']['profile_pic_url'])

            return profile

        else:
            return None

    def get_followingNames(self, userId, max_id):

        following_response = self.client.user_following(userId, max_id=max_id)
        # logger.info(following_response)
        following_names = []
        for following in following_response['users']:
            following_names.append(following['username'])

        max_id = following_response.get('next_max_id')

        return following_names, max_id

def main():
    # Init
    if not accounts_over5k.find_one():
        index = 1
        user_info = service.get_profile_over50k(start_username)
        user_info['user_id'] = index
        accounts_over5k.update({'id': user_info['id']}, {"$set": user_info}, upsert=True)

        data = {'selector': 0, 'index': 1}
        with open('json', 'w') as f:
            json.dump(data, f)

    # accounts_over5k.insert(user_info)

    with open('json') as f:
        data = json.load(f)
    selector = data['selector']
    index = data['index']

    while True:
        selector += 1
        data = {'selector': selector, 'index': index}
        with open('json', 'w') as f:
            json.dump(data, f)
        try:
            c_userId = accounts_over5k.find_one({"user_id": selector}).get('id')
        except:
            c_userId = accounts_over5k.find_one({"user_id": selector+1}).get('id')

        logger.info("\n")
        logger.info(selector)
        logger.info(accounts_over5k.find_one({"user_id": selector}).get('username'))
        logger.info("followings %d" %accounts_over5k.find_one({"user_id": selector}).get('followings'))
        logger.info("\n")

        maxId = 0
        while True:
            try:
                followingNames, maxId = service.get_followingNames(c_userId, maxId)
            except Exception as e:
                logger.info(e)
                sleep(100)
                continue
            # logger.info(maxId)

            for following_name in followingNames:
                if not accounts_over5k.find_one({"username": following_name}):
                    logger.info("candidate account: %s" %following_name)
                    try:
                        user_info = service.get_profile_over50k(following_name)
                    except Exception as e:
                        logger.info(e)
                        sleep(100)
                        continue

                    if user_info is not None:
                        index += 1
                        data = {'selector': selector, 'index': index}
                        with open('json', 'w') as f:
                            json.dump(data, f)

                        user_info['user_id'] = index
                        accounts_over5k.update({'id': user_info['id']}, {"$set": user_info}, upsert=True)

                        logger.info(index)
                        logger.info(following_name)
                        logger.info(user_info['followers'])

            if maxId is None or type(maxId)==str:
                break

if __name__ == "__main__":
    # Making logger cutomized
    import logging
    from logging.handlers import RotatingFileHandler

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    logFile = './log'
    my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    logger.addHandler(my_handler)


    # Get username and password from config.py
    username = username
    password = password
    # email_regex = email_regex

    # client = MongoClient(host, port)
    # db = client.instagram
    # accounts_over5k = db.accounts_over5k
    # accounts_over5k.create_index([('user_id', ASCENDING)], unique=True)
    #
    # # Generate Instagram_DataService object with above username and password
    # while True:
    #     try:
    #         service = Instagram_DataService(username, password)
    #         break
    #     except Exception as e:
    #         logger.info(e)
    #         sleep(100)
    #
    # email_regex = re.compile(r'[\w\.-]+@[\w\.-]+')
    # logger.info('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format('abc'))

    # main()

    service = Instagram_DataService(username, password)
    print (service.client.user_info(service.user_id))



