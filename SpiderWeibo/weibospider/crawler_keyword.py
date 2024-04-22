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
from config import INPUT_TASK


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
    process.crawl(mode_to_spider['tweet_by_keyword'], 
                  keywords=INPUT_TASK['KEYWORDS'], 
                  st_y=INPUT_TASK['ST_Y'], 
                  st_mth=INPUT_TASK['ST_MTH'], 
                  st_day=INPUT_TASK['ST_DAY'], 
                  end_y=INPUT_TASK['END_Y'], 
                  end_mth=INPUT_TASK['END_MTH'], 
                  end_day=INPUT_TASK['END_DAY']
                  )
    # process.crawl(mode_to_spider['tweet_by_tweet_id'], tweet_ids=['5022486381729038'])
    # # the script will block here until the crawling is finished
    process.start()
    # process.stop()

    