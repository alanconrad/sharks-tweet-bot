"""
See Twitter API documentation: http://docs.tweepy.org/en/v3.5.0/
"""
import json
import tweepy
from TwitterBot import TweetBot
import requests as r
from bs4 import BeautifulSoup

with open('credentials.json') as f:
    credentials = json.loads(f.read())

CONSUMER_KEY = credentials['consumer_key']
CONSUMER_SECRET_KEY = credentials['consumer_secret_key']
ACCESS_TOKEN = credentials['access_token_key']
ACCESS_SECRET_TOKEN = credentials['access_token_secret_key']

# SJ Sharks News Twitter Bot class
# Subclass of TweetBot super class
class SharksTweetBot(TweetBot):
    # Returns list of html containers from the 10 most recenet articles on nhl.com/sharks/news
    def get_containers(self, url):
        response = r.get(url)
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
            articles = []
            tweeted = False
            # Check if article name matches any previous tweet
            for tweet in tweets:
                if article_name in tweet:
                    tweeted = True
                    break
            # Tweet if no previous tweet contained the article_name
            if tweeted == False:
                articles.add([article_name, article_link])
        return articles

    # Retweets a tweet if it detects the tweet contains both the hashtag and keyword
    # keywords: string
    # hashtag: string
    # num_tweets: int number of tweets to get. MAX -> 100
    def retweet_tweets(self, hashtag, keyword, num_tweets):
        num_retweets = 0
        for tweet in tweepy.Cursor(self.api.search, q=hashtag, count=num_tweets, include_entities=True).items(num_tweets):
            if keyword in tweet.text:
                self.api.retweet(tweet.id)
                print("Retweeted tweet id: " + tweet.id)
                num_retweets += 1
        result = "Number of tweets retweeted: " + str(num_retweets)
        return result

# Entry point
def main():
    url = "https://www.nhl.com/sharks/news"
    bot = SharksTweetBot(CONSUMER_KEY, CONSUMER_SECRET_KEY, ACCESS_TOKEN, ACCESS_SECRET_TOKEN)
    containers = bot.get_containers(url)
    articles = bot.scan_containers(containers)
    result = bot.tweet_articles(articles)
    bot.follow_followers()
    print(result)
    bot.like_hashtags(['SJSharks'], 10)


if __name__ == "__main__":
    main()