from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.tweet_by_user_id import TweetSpiderByUserID
from spiders.tweet_by_keyword import TweetSpiderByKeyword
from spiders.tweet_by_tweet_id import TweetSpiderByTweetID
from spiders.comment import CommentSpider
from spiders.follower import FollowerSpider
from spiders.user import UserSpider
from spiders.fan import FanSpider
from spiders.repost import RepostSpider
import os
import glob
import pandas as pd
import json


def jsonl_to_dataframe(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return pd.DataFrame(data)


def user_2_user_id(user:dict):
    # user = eval(user)
    return user['_id']


if __name__ == '__main__':

    # mode = sys.argv[1]
    user_ids = ['1749127163']
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings'
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    mode_to_spider = {
        'comment': CommentSpider,
        'fan': FanSpider,
        'follow': FollowerSpider,
        'user': UserSpider,
        'repost': RepostSpider,
        'tweet_by_tweet_id': TweetSpiderByTweetID,
        'tweet_by_user_id': TweetSpiderByUserID,
        'tweet_by_keyword': TweetSpiderByKeyword,
    }
   

    # 运行新的爬虫
    tweets_key_word = glob.glob('../output/*tweet_spider_by_keyword*.jsonl')
    # 排序取最大的
    tweets_key_word.sort()
    tweets_key_word = tweets_key_word[-1]
    tweets_key_word_df = jsonl_to_dataframe(tweets_key_word)

    # 获取新任务
    tweets_is_retweet = tweets_key_word_df.loc[tweets_key_word_df['is_retweet']]
    tweets_id_need = tweets_is_retweet.loc[tweets_is_retweet['retweet_id'].isin(tweets_key_word_df['_id']) == False]
    tweet_ids = list(tweets_id_need['retweet_id'].unique())

    # 运行新的爬虫
    process = CrawlerProcess(settings)
    process.crawl(mode_to_spider['tweet_by_tweet_id'], tweet_ids=tweet_ids)
    process.start()




    