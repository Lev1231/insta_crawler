import os
import json
import codecs
import functools

from Instagram import api
try:
    from Instagram.instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from Instagram.instagram_private_api import (
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

class InstagramClient():
    '''Main class of the project'''
    def __init__(self, username, password, settings_file_path):
        '''
        :param username: Instagram Login Username
        :param password: Instagram Login Password
        '''
        device_id = None
        try:
            settings_file = settings_file_path
            if not os.path.isfile(settings_file):
                # settings file does not exist
                print('Unable to find file: {0!s}'.format(settings_file))

                # login new
                self.main = Client(
                    username, password,
                    on_login=lambda x: onlogin_callback(x, settings_file))
            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=from_json)
                print('Reusing settings: {0!s}'.format(settings_file))

                device_id = cached_settings.get('device_id')
                # reuse auth settings
                self.main = Client(
                    username, password,
                    settings=cached_settings)

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

            # Login expired
            # Do relogin but use default ua, keys and such
            self.main = Client(
                username, password,
                device_id=device_id,
                on_login=lambda x: onlogin_callback(x, settings_file))

        except ClientLoginError as e:
            print('ClientLoginError {0!s}'.format(e))
            exit(9)
        except ClientError as e:
            print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            exit(9)
        except Exception as e:
            print('Unexpected Exception: {0!s}'.format(e))
            exit(99)

        self.user_id = self.main.username_info(username)['user']['pk']

        # client = MongoClient(host, port)
        # self.db = client.instagram

    def userId(self, username):

        return self.main.username_info(username)['user']['pk']

    def last_photos(self, user_id):
        '''
        :param user_id: pk of user in instagram
        '''

        max_id = 0

        post_response = self.main.user_feed(user_id, max_id=max_id)
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
        user_info = self.main.username_info(username)

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
                profile['last_photos'] = self.last_photos(profile['id'])
            except ClientError:
                profile['last_photos'] = {}

            return profile

        else:
            return None

    def followings(self, userId, max_id=None):
        following_response = self.main.user_following(userId, max_id=max_id)
        # logger.info(following_response)

        for following in following_response['users']:
            yield following['username']

        max_id = following_response.get('next_max_id')

        if max_id:
            print ("MAX ID: %s" %max_id)
            self.followings(userId, max_id)

    def likes_comments(self, username):
        feeds = self.main.username_feed(username)['items']
        if len(feeds) > 0:
            likes = map(lambda x: x.get('like_count', 0), feeds)
            comments = map(lambda x: x.get('comment_count', 0), feeds)

            avg_likes = int(functools.reduce(lambda x, y: x + y, likes) / len(feeds))
            avg_comments = int(functools.reduce(lambda x, y: x + y, comments) / len(feeds))
        else:
            avg_comments = 0
            avg_likes = 0

        return avg_likes, avg_comments

    def info(self, username):
        profile = self.main.username_info(username)
        user = profile['user']
        username = username
        full_name = user.get('full_name', '')
        bio = user.get("biography", '')

        follower_count = user.get('follower_count')

        avg_likes, avg_comments = self.likes_comments(username)
        engagement = round((avg_likes + avg_comments)/follower_count,2) * 100

        language_spoken = api.languageDetection(bio)
        gender = api.genderDetectionByName(full_name.encode('utf-8'))
        location = ''

        return [username, language_spoken, gender, location, follower_count, avg_likes, avg_comments, engagement]
