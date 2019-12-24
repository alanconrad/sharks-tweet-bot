# Super class for a twitter bot
import json
import tweepy

# Read credential keys
with open('credentials.json') as f:
    credentials = json.loads(f.read())

CONSUMER_KEY = credentials['consumer_key']
CONSUMER_SECRET_KEY = credentials['consumer_secret_key']
ACCESS_TOKEN = credentials['access_token_key']
ACCESS_SECRET_TOKEN = credentials['access_token_secret_key']

# SJ Sharks News Twitter Bot class
class TweetBot:
    # Initializes instance
    def __init__(self, consumer_key, consumer_secret_key, access_token, access_secret_token):
        self.consumer_key = consumer_key
        self.consumer_secret_key = consumer_secret_key
        self.access_token = access_token
        self.access_secret_token = access_secret_token
        # Attempts to authenticate into the client using Twitter's OAuth
        try:
            self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret_key)
            self.auth.set_access_token(self.access_token, self.access_secret_token)
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
    # screen_name: user id / username of profile to retrieve
    def get_last_tweet(self, screen_name):
        tweet = self.client.user_timeline(id = screen_name, count = 1)[0]
        return tweet.text

    # Tweets inputted article name and link
    def tweet_articles(self, articles):
        for article in articles:
            tweet = article_name + '\n' + article_link
            self.client.update_status(tweet)
        result = str(len(articles)) + " number of articles tweeted."
        return result

     # Follows any follower that the bot is currently not following
    def follow_followers(self):
        for follower in tweepy.Cursor(self.api.followers).items():
            status = self.api.show_friendship(source_screen_name=self.api.me().screen_name, target_screen_name=follower.screen_name)
            if status == False:
                follower.follow()
                print(follower.screen_name)
            else:
                print("Already follow " + follower.screen_name)

    # Favorites 
    def like_hashtags(self, hashtags, num_tweets):
        for hashtag in hashtags:
            hashtag = '#' + hashtag
            for tweet in tweepy.Cursor(self.api.search, q=hashtag, count=num_tweets, include_entities=True).items(num_tweets):
                username = tweet.user.name
                try:
                    self.api.create_favorite(tweet.id)
                    print("Gave a like to " + username)
                except:
                    print("Already liked " + username + "'s tweet.")

    # Tweets a tweet of the inputted string: text
    def update_status(text):
        self.client.update_status(text)

    # Follows inputted username
    def follow_user(username):
        try:
            self.api.create_friendship(username)
        except:
            print("Not a valid username!")

    # Unfollows inputted username
    def unfollow_user(username):
        try:
            self.api.destroy_friendship(username)
        except:
            print("Not a valid username!")

    # Tweets file along with
    def tweet_media(file, text):
        try:
            self.api.update_with_media(filename=file, status=text)
        except:
            print("File does not exist!")