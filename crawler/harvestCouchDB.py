from tweepy import API 
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
 
import twitter_credentials
import json
import couchdb
import time

import modifyTweet
from textblob import TextBlob

# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

class SentimentAnalyser():

    def analyse(self, data):
        blob = TextBlob(data)

        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        print(data)
        print(blob.sentiment)
        return [polarity,subjectivity]


class CouchDB():

    def __init__(self):
        couch = couchdb.Server('http://127.0.0.1:5984/')
        couch.resource.credentials = ("camizous", "camizous1109")
        if "tweet_raw" in couch:
            self.db = couch['tweet_raw']
        else:
            self.db = couch.create('tweet_raw')

    def addDoc(self, data): 
        tweet = json.loads(data)
        sentimentAnalyer = SentimentAnalyser()
        sentiment = sentimentAnalyer.analyse(tweet['text'])
        self.db.save({'coordinates':tweet['coordinates'],
                      'created_at':tweet['created_at'],
                      'place':tweet['place'],
                      'user':{'id':tweet['user']['id'],
                              'name':tweet['user']['name'],
                              'id_str':tweet['user']['id_str'],
                              'description':tweet['user']['description']},
                      'lang':tweet['lang'],
                      'text':tweet['text'],
                      'sentiment':{
                          'polarity':sentiment[0],
                          'subjectivity':sentiment[1]
                      }})


# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()
        self.error_num = 0    

    def stream_tweets(self, fetched_tweets_filename):
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app() 
        stream = Stream(auth, listener)
        while True:
            try:
                stream.filter(locations=[112.15, -44.84 ,155.65, -11])
                break
            except Exception as e:
                print(e)
                self.error_num += 1
                print("ERROR---Sleeping", self.error_num)
                time.sleep(60)


# # # # TWITTER STREAM LISTENER # # # #
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
        self.couchDB = CouchDB()
        self.count = 0

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            country = tweet["place"]["country"]
            print(country, self.count)
            self.count +=1
            modifiedData = modifyTweet.check(data)
            if modifiedData:
                self.couchDB.addDoc(modifiedData)
                print("Upload successfully")
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True
          
    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)

 
if __name__ == '__main__':
 
    # Authenticate using config.py and connect to Twitter Streaming API.
    fetched_tweets_filename = "result_geo_aus_5.json"

    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(fetched_tweets_filename)


    
    
    

    