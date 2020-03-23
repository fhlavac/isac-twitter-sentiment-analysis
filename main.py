import tweepy
import re

from google.cloud import language
from google.cloud import language_v1
from google.cloud.language import enums
from google.cloud.language import types
from datetime import datetime, timedelta
from nltk.tokenize import WordPunctTokenizer

ACC_TOKEN = ''
ACC_SECRET = ''
CONS_KEY = ''
CONS_SECRET = ''


def authentication(cons_key, cons_secret, acc_token, acc_secret):  # Tweepy authentication
    auth = tweepy.OAuthHandler(cons_key, cons_secret)
    auth.set_access_token(acc_token, acc_secret)
    api = tweepy.API(auth)
    return api


"""
def search_tweets(keyword, total_tweets):   # keyword number of wanted tweets since yesterday
    today_datetime = datetime.today().now()
    yesterday_datetime = today_datetime - timedelta(days=1)
    today_date = today_datetime.strftime('%Y-%m-%d')
    yesterday_date = yesterday_datetime.strftime('%Y-%m-%d')
    api = authentication(CONS_KEY, CONS_SECRET, ACC_TOKEN, ACC_SECRET)
    search_result = tweepy.Cursor(api.search,
                                  q=keyword,
                                  since=yesterday_date,
                                  result_type='popular',
                                  tweet_mode='extended',
                                  lang='en').items(total_tweets)
    return search_result
"""


def users_tweets(username, total_tweets):  # keyword number of wanted tweets since yesterday
    today_datetime = datetime.today().now()
    last_year_datetime = today_datetime - timedelta(days=3000)
    today_date = today_datetime.strftime('%Y-%m-%d')
    last_year_datetime = last_year_datetime.strftime('%Y-%m-%d')
    api = authentication(CONS_KEY, CONS_SECRET, ACC_TOKEN, ACC_SECRET)
    user = api.get_user(username)
    print(user.name + '\n')
    search_result = []
    for page in tweepy.Cursor(api.user_timeline,
                              id=username,
                              result_type='recent',
                              tweet_mode='extended',
                              lang='en',
                              count=500).pages():
        for tweet in page:
            search_result.append(tweet)
    return search_result[:680]


def clean_tweet(tweet):
    user_removed = re.sub(r'@[A-Za-z0-9]+', '', tweet.decode('utf-8'))  # remove users
    link_removed = re.sub('https?://[A-Za-z0-9./]+', '', user_removed)  # remove links
    number_removed = re.sub('[^a-zA-Z]', ' ', link_removed)  # remove numbers
    lower_case_tweet = number_removed.lower()  # make lowercase
    tok = WordPunctTokenizer()
    words = tok.tokenize(lower_case_tweet)
    print(words)
    clean_tweet = (' '.join(words)).strip()  # creates string with spaces with leading and trailing characters removed
    return clean_tweet


def prepare_tweets(tweets):
    prepared = []
    for tweet in tweets:
        try:
            prepared.append(clean_tweet(tweet.retweeted_status.full_text.encode('utf-8')))
        except AttributeError:  # Not a retweet
            prepared.append(clean_tweet(tweet.full_text.encode('utf-8')))
    return list(dict.fromkeys(prepared))


def get_sentiment_score(tweet):
    client = language.LanguageServiceClient()
    document = types \
        .Document(content=tweet,
                  type=enums.Document.Type.PLAIN_TEXT, language='en')
    score = client.analyze_sentiment(document, encoding_type=enums.EncodingType.UTF8).document_sentiment.score
    return score


def analyze_tweets_sentiment(tweets, username):
    score = 0
    negative = 0
    neutral = 0
    positive = 0
    index = 0
    f = open(username + ".txt", "a")
    for tweet in tweets:
        index += 1
        score += get_sentiment_score(tweet)
        f.write(format(tweet) + ';' + str(format(get_sentiment_score(tweet)) + '\n'))
        print(index, ' ', str(len(tweets)), tweet)
        print(get_sentiment_score(tweet), '\n')
        if get_sentiment_score(tweet) <= -0.25:
            negative += 1
        elif get_sentiment_score(tweet) <= 0.25:
            neutral += 1
        else:
            positive += 1
    final_score = round((score / float(len(tweets))), 2)
    f.write('TWEETS COUNT: ' + str(len(tweets)) + '\n')
    print('TWEETS COUNT: ', len(tweets))
    f.write('FINAL SCORE: ' + str(final_score) + '\n')
    print('FINAL SCORE: ', final_score)
    f.write('NEUTRAL: ' + str(neutral) + '\n')
    print('NEUTRAL: ', neutral)
    f.write('NEGATIVE: ' + str(negative) + '\n')
    print('NEGATIVE: ', negative)
    f.write('POSITIVE: ' + str(positive) + '\n')
    print('POSITIVE: ', positive)
    f.close()
    return final_score


"""
def get_entity_sentiment_score(tweet):
    client = language_v1.LanguageServiceClient()
    type_ = enums.Document.Type.PLAIN_TEXT  # HTML possible as well
    language = "en"
    document = {"content": tweet, "type": type_, "language": language}    # language automatically detected
    encoding_type = enums.EncodingType.UTF8
    response = client.analyze_entity_sentiment(document, encoding_type=encoding_type)

    for entity in response.entities:
        if enums.Entity.Type(entity.type).name == 'PERSON' and entity.name == 'andrej babis':
            return entity.sentiment.score
    return None


def analyze_tweets_entity_sentiment(keyword, total_tweets):
    score = 0
    tweets = prepare_tweets(search_tweets(keyword, total_tweets))
    count = len(tweets)
    for tweet in tweets:
        entity_sentiment_score = get_entity_sentiment_score(tweet)
        if entity_sentiment_score != None:
            score += entity_sentiment_score
            print('Tweet: {}'.format(tweet))
            print('Score: {}\n'.format(entity_sentiment_score))
        else:
            count -= 1
    final_score = round((score / float(count)), 2)
    print('count:', count)
    return final_score


if __name__ == '__mdain__':

    keyword = 'Andrej Babiš'

    final_score = analyze_tweets_entity_sentiment(keyword, 30)

    if final_score <= -0.25:
        status = 'NEGATIVE ❌'
    elif final_score <= 0.25:
        status = 'NEUTRAL ?'
    else:
        status = 'POSITIVE ✅'
    print('Average score for '
          + str(keyword)
          + ' is '
          + str(final_score)
          + ' '
          + status)


if __name__ == '__main__':

    keyword = '@PREZIDENTmluvci'

    final_score = analyze_tweets_sentiment(keyword, 100)

    if final_score <= -0.25:
        status = 'NEGATIVE ❌'
    elif final_score <= 0.25:
        status = 'NEUTRAL ?'
    else:
        status = 'POSITIVE ✅'
    print('Average score for '
          + str(keyword)
          + ' is '
          + str(final_score)
          + ' '
          + status)
"""
if __name__ == '__main__':

    username = '@cnnbrk'

    tweets = prepare_tweets(users_tweets(username, 200))

    final_score = analyze_tweets_sentiment(tweets, username)

    if final_score <= -0.25:
        status = 'NEGATIVE ❌'
    elif final_score <= 0.25:
        status = 'NEUTRAL ?'
    else:
        status = 'POSITIVE ✅'
    print('Average score is '
          + str(final_score)
          + ' '
          + status)
