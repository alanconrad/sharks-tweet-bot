"""
See Twitter API documentation: http://docs.tweepy.org/en/v3.5.0/
"""
import json
import tweepy
import requests as r
from bs4 import BeautifulSoup

with open('credentials.json') as f:
    credentials = json.loads(f.read())

CONSUMER_KEY = credentials['consumer_key']
CONSUMER_SECRET_KEY = credentials['consumer_secret_key']
ACCESS_TOKEN = credentials['access_token_key']
ACCESS_SECRET_TOKEN = credentials['access_token_secret_key']

# SJ Sharks News Twitter Bot class
class SharksTweetBot:
    def __init__(self):
        self.consumer_key = CONSUMER_KEY
        self.consumer_secret_key = CONSUMER_SECRET_KEY
        self.access_token = ACCESS_TOKEN
        self.access_secret_token = ACCESS_SECRET_TOKEN
        # Tries to authenticate into the client
        try:
            self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
            self.auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET_TOKEN)
            self.api = tweepy.API(self.auth)
            self.client = tweepy.API(self.auth)
            if not self.client.verify_credentials():
                raise tweepy.TweepError
        except tweepy.TweepError as e:
            print('ERROR : connection failed. Check your OAuth keys.')
        else:
            print('Connected as @{}'.format(self.client.me().screen_name))
            self.client_id = self.client.me().id

    # Returns the most recent tweet from the client
    def get_last_tweet(self):
        tweet = self.client.user_timeline(id = self.client_id, count = 1)[0]
        return tweet.text

    # Returns list of html containers from the 10 most recenet articles on nhl.com/sharks/news
    def get_containers(self):
        response = r.get('https://www.nhl.com/sharks/news')
        page_html = BeautifulSoup(response.text, 'html.parser')
        containers = page_html.find_all('article', class_ = 'article-item')
        return containers

    # Parses through the containers to extract article name & link
    # Article & link will be tweeted if it hasn't been tweeted yet
    def scan_containers(self, containers):
        tweets = self.client.user_timeline(id = self.client_id)
        tweets = [t.text for t in tweets]
        num_tweets = 0
        # Loop through containers
        for i in range(len(containers)):
            article_name = containers[i].find('h1', class_ = 'article-item__headline').text
            article_link = 'nhl.com' + containers[i].find('div', class_ = 'social-share__wrapper').attrs['data-share-url']
            tweeted = False
            # Check if article name matches any previous tweet
            for tweet in tweets:
                if article_name in tweet:
                    tweeted = True
                    break
            # Tweet if no previous tweet contained the article_name
            if tweeted == False:
                self.tweet_article(article_name, article_link)
                num_tweets += 1
        result_msg = 'Number of articles tweeted:', num_tweets
        return result_msg

    # Tweets inputted article name and link
    def tweet_article(self, article_name, article_link):
        tweet = article_name + '\n' + article_link
        self.client.update_status(tweet)

    # Follows any follower that the bot is currently not following
    def follow_followers(self):
        for follower in tweepy.Cursor(self.api.followers).items():
            status = self.api.show_friendship(source_screen_name=self.api.me().screen_name, target_screen_name=follower.screen_name)
            if status == False:
                follower.follow()
                print(follower.screen_name)
            else:
                print("Already follow " + follower.screen_name)

    # Favorites tweets that contain x in hashtags
    # Count = number of recent tweets to scan
    def like_hashtags(self, hashtags):
        for hashtag in hashtags:
            hashtag = '#' + hashtag
            for tweet in tweepy.Cursor(self.api.search, q=hashtag, count=10, include_entities=True).items(10):
                username = tweet.user.name
                try:
                    self.api.create_favorite(tweet.id)
                    print("Gave a like to " + username)
                except:
                    print("Already liked " + username + "'s tweet.")

# Entry point
def lambda_handler(_event_json, _context):
    bot = SharksTweetBot()
    containers = bot.get_containers()
    result = bot.scan_containers(containers)
    bot.follow_followers()
    print(result)
    bot.like_hashtags(['SharksTweetBot'])