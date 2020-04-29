#可以挖掘标注澳大利亚地理位置的tweet，不过很慢，几分钟才有一条数据
import tweepy
from key import *
import json


class myListener(tweepy.StreamListener):
    def on_data(self, raw_data):
        self.process_data(raw_data)
        return True

    def process_data(self, raw_data):
        twitter = json.loads(raw_data)
        if twitter["geo"]:
            print(raw_data)

    def on_error(self, status_code):
        if status_code == 420:
            return False


class myStream():
    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self, keyword):
        self.stream.filter(track=keyword)


if __name__ == "__main__":
    listener = myListener()

    auth = tweepy.OAuthHandler(API, API_secret_key)
    auth.set_access_token(Access_token, Access_token_secret)

    stream = myStream(auth, listener)
    stream.start(['happiness'])
