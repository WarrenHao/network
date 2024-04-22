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
    # process.crawl(mode_to_spider['tweet_by_keyword'], keywords=['秦朗事件'], st_y=2024, st_mth=3, st_day=15, end_y=2024, end_mth=4, end_day=20)
    # process.crawl(mode_to_spider['tweet_by_tweet_id'], tweet_ids=['5022486381729038'])
    # # the script will block here until the crawling is finished
    # process.start()
    # process.stop()

    # 运行新的爬虫
    tweets_key_word = glob.glob('../output/*tweet_spider_by_keyword*.jsonl')
    # 排序取最大的
    tweets_key_word.sort()
    tweets_key_word = tweets_key_word[-1]
    tweets_key_word_df = jsonl_to_dataframe(tweets_key_word)



    # 获取用户id
    tweets_tweet_id = glob.glob('../output/*tweet_spider_by_tweet_id*.jsonl')
    tweets_tweet_id.sort()
    tweets_tweet_id = tweets_tweet_id[-1]
    tweets_tweet_id_df = jsonl_to_dataframe(tweets_tweet_id)

    tweets_all = pd.concat([tweets_key_word_df, tweets_tweet_id_df], axis=0)

    user_ids = tweets_all['user'].apply(user_2_user_id).tolist()
    # 去重
    user_ids = list(set(user_ids))

    # 运行新的爬虫
    process = CrawlerProcess(settings)
    process.crawl(mode_to_spider['user'], user_ids=user_ids)
    process.start()




    