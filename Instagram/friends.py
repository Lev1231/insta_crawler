import os

import pandas as pd

from .config import *
from .utility import *
from .logger import friend_logger
from .insta import InstagramClient


def start_points():
    if os.path.join(output_csv):
        df = pd.read_csv(output_csv)
        g = df.groupby(['username'])
        index1 = len(g) - 1
        index2 = len(g.get_group(g.last().iloc[-1].name)) - 1

        return index1, index2
    else:
        return 0, 0

def main():
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

            insta_client.info(following)

            index2 += 1

        index2 = 0
        index1 += 1


if __name__ == "__main__":
    user_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'japan_username.csv')
    insta_client = InstagramClient(username, password, settings_file_path)

    output_csv = os.path.join('output', 'friends.csv')
    header = ['Username', 'Language Spoken', 'Gender', 'Location', 'Followers', 'Average likes', 'Average Comments', 'Engagement']

    if not os.path.exists(output_csv):
        createCsv(output_csv, header)

    main()

    # insta_client.info('watanabenaomi703')


