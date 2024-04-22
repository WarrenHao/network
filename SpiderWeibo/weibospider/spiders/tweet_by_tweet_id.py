#!/usr/bin/env python
# encoding: utf-8
"""
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/14
"""
import json
from scrapy import Spider
from scrapy.http import Request
from spiders.common import parse_tweet_info, parse_long_tweet


class TweetSpiderByTweetID(Spider):
    """
    用户推文ID采集推文
    """
    name = "tweet_spider_by_tweet_id"
    base_url = "https://weibo.cn"

    def __init__(self, tweet_ids: list, **kwargs):
        super(TweetSpiderByTweetID, self).__init__(**kwargs)
        self.tweet_ids = tweet_ids
       

    def start_requests(self):
        """
        爬虫入口
        """
        # 这里user_ids可替换成实际待采集的数据
        tweet_ids = self.tweet_ids
        for tweet_id in tweet_ids:
            url = f"https://weibo.com/ajax/statuses/show?id={tweet_id}"
            yield Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        data = json.loads(response.text)
        item = parse_tweet_info(data)
        if item['isLongText']:
            url = "https://weibo.com/ajax/statuses/longtext?id=" + item['mblogid']
            yield Request(url, callback=parse_long_tweet, meta={'item': item})
        yield item
