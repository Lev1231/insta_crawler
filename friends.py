import os
import sys
import time
import random
import pickle
import socket
import urllib
import argparse

import pandas as pd

from Instagram.config import *
from Instagram.utility import *
from Instagram.logger import friend_logger
from Instagram.insta import InstagramClient
from Instagram.insta import ClientLoginError, ClientError


def updateIndex(index1,index2):
    with open("index.pkl", 'wb') as f:
        pickle.dump({'index1': index1, 'index2': index2}, f)

def start_points():
    if os.path.exists('index.pkl'):
        with open("index.pkl", 'rb') as f:
            dict = pickle.load(f)

        return dict['index1'], dict['index2']+1

    else:
        return 0, 0

def main():
    global insta_client

    df = pd.read_csv(user_csv)
    df = df[df.status==0]

    usernames = list(df.username)

    index1, index2 = start_points()

    while index1 < len(usernames):
        username = usernames[index1]

        friend_logger.info ("USERNAME: %s" %username)

        user_id = insta_client.userId(username)
        followings = list(insta_client.followings(user_id))

        friend_logger.info ("Count of the Followings: %d" %len(followings))

        while index2 < len(followings):
            following = followings[index2]

            friend_logger.info ("Following_%d : %s" %(index2, following))

            try:
                info = insta_client.info(following)
                if not langs:
                    if info[4] > int(followerNumbers):
                        friend_logger.info("Added: " + str(info))
                        addRowCsv(output_csv, info)
                    else:
                        friend_logger.info("Ignored: " + str(info))
                else:
                    if info[4] > int(followerNumbers) and set(langs).intersection([item.split(":")[0] for item in info[1].split(",")]):
                        friend_logger.info("Added: " + str(info))
                        addRowCsv(output_csv, info)
                    else:
                        friend_logger.info("Ignored: " + str(info))

                updateIndex(index1, index2)

                time.sleep(random.randint(5,10))

                index2 += 1

            except ClientLoginError as e:
                friend_logger.error(e)
                friend_logger.error("Please check your account")

                sys.exit()

            except ClientError as e:
                friend_logger.error(e)

                index2 += 1

            except (socket.timeout, ConnectionResetError , urllib.error.URLError) as e:
                friend_logger.error(e)
                time.sleep(600)
                insta_client = InstagramClient(username, password, settings_file_path)

            finally:
                pass

        index2 = 0
        index1 += 1

if __name__ == "__main__":
    user_csv = os.path.join(os.path.dirname(__file__), 'db', 'japan_username.csv')
    insta_client = InstagramClient(username, password, settings_file_path)

    output_csv = os.path.join(os.path.dirname(__file__), 'output', 'friends.csv')
    header = ['Username', 'Language Spoken', 'Gender', 'Location', 'Followers', 'Average likes', 'Average Comments', 'Engagement']

    if not os.path.exists(output_csv):
        try:
            os.mkdir(os.path.dirname(output_csv))
        except:
            pass

        createCsv(output_csv, header)

    parser = argparse.ArgumentParser(description="Instagram Crawler")
    parser.add_argument('--langs', help='Spoken language ex: ja/kr/vn', default=langs )
    parser.add_argument('--follwerNumbers', help='The script find the people who has folleres more than this value. ex: 4000', default=followerNumbers)

    args = parser.parse_args()
    if langs:
        langs = args.langs.split("/")
    followerNumbers = args.follwerNumbers

    main()

    # print (insta_client.main.username_info('kiyochamcham'))
    # print (insta_client.info('kiyochamcham'))



