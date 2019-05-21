import requests
import os
import json
import logging
import secrets
import urllib.parse
import datetime
from hashlib import sha1
from requests_oauthlib import OAuth1
import sys
from sentiment import SentimentAnalyzer


directory_root = '/Users/gpanez/Documents/tweets/BBCPolitics'


class Tweet:
    def __init__(self, tweet_json):
        self.__tweet_json = tweet_json
        self.hs = {'screen_name': tweet_json['user']['screen_name'],
                   'id': tweet_json['id'],
                   'id_str': tweet_json['id_str'],
                   'text': tweet_json['text'],
                   'created_at': tweet_json['created_at']}

    def save(self):
        dt = datetime.datetime.strptime(self.hs['created_at'], '%a %b %d %H:%M:%S %z %Y')
        dt_str = dt.strftime("%Y%m%d")
        directory = directory_root + '/' + dt_str
        if not os.path.exists(directory):
            logging.debug('Creating directory: [%s]', directory)
            os.makedirs(directory)

        try:
            with open(directory + '/' + self.hs['id_str'] + '.txt', "w") as file:
                json.dump(self.hs, file)
        except IOError:
            logging.error('Couldn\'t create the file: [%s]', directory + '/' + self.hs['id_str'] + '.txt')

    def __str__(self):
        return json.dumps(self.hs)


# ----


def load_config():
    try:
        with open(directory_root + '/config.txt', "r") as file:
            config = json.load(file)
            if config is not None:
                return config['since_id']
    except IOError:
        logging.error('Couldn\'t load the file: [%s]', directory_root + '/config.txt')
    return None


def save_config(since_id):
    try:
        with open(directory_root + '/config.txt', "w") as file:
            config = {'since_id': since_id}
            json.dump(config, file)
    except IOError:
        logging.error('Couldn\'t create/update the file: [%s]', directory_root + '/config.txt')


def get_tweets(since_id):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

    # OAuth1(YOUR_APP_KEY', 'YOUR_APP_SECRET', 'USER_OAUTH_TOKEN', 'USER_OAUTH_TOKEN_SECRET')
    auth = OAuth1('1QUYxqT3fLJzznjF6qubfCU8N', 'Vnt2uyXpbRWABCVz6W3r70ZiS3T7sm3jIMHyoTTuiMAgPuK8hE',
                  '1112706472360771588-b5xCR7oQn6dB0brCADkJvh0ejUKtSc', 'J1DevmDejLeaI3DaLG5xbnYKNvrh1yMtw7irmcko4tU0r')

    payload = {'screen_name': 'BBCPolitics',
               'count': 200,
               'exclude_replies': True,
               'include_rts': False}

    if since_id is not None:
        payload['since_id'] = since_id
        new_since_id = since_id
    else:
        new_since_id = -1

    max_id = sys.maxsize
    first_req = True

    while True:
        if not first_req:
            payload['max_id'] = max_id

        r = requests.get(url, auth=auth, params=payload)
        if r.status_code == 200:
            tweets_json = r.json()
            if len(tweets_json) == 0:
                break
            else:
                first_req = False

            for tweet in tweets_json:
                Tweet(tweet).save()
                if tweet['id'] < max_id:
                    max_id = tweet['id']
                if tweet['id'] > new_since_id:
                    new_since_id = tweet['id']
            max_id -= 1
        else:
            logging.debug("API response wasn't successful")
            logging.debug(str(r))
    logging.debug("Saving new since_id: " + str(new_since_id))
    save_config(new_since_id)


def main():
    logging.basicConfig(filename=directory_root + '/log.txt',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logging.info("Tweets Collector ")
    logging.getLogger('TCBBC')

    #since_id = load_config()
    #get_tweets(since_id)
    s = SentimentAnalyzer()
    text = "Labour lies. Labour are Remain party. They blame Austerity for lack of housing, policing, education, Low minimum wage. But 350,000 low skilled immigrants net into UK is the real reason there is a major strain on public services & housing. It's not rocket science it's common sense"
    score, category = s.analyze(text)
    print("score: {}, category: {}".format(score, category))
    # TODO: Added timing thresholds but need to add limit per day
    # TODO: Added timing thresholds but need to add saving the queue
    # TODO: Need to add cron job, and overall begin and end


if __name__ == "__main__":
    main()
    print("done")
