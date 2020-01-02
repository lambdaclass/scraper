# -*- coding: utf-8 -*-

# Custom extensions

import socket
from datetime import datetime, timedelta, timezone

import requests
from scrapy import signals
from scrapy.exceptions import NotConfigured


class SlackNotification:
    """Slack notification extension based on https://github.com/rudeigerc/scrapy-slackbot"""
    def __init__(self, name, emoji, webhook, channel, stats):
        self.name = name
        self.emoji = emoji
        self.webhook = webhook
        self.channel = channel
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        name = crawler.settings.get('SLACK_BOT_NAME', 'Scrapybot')
        emoji = crawler.settings.get('SLACK_EMOJI', ':taleb:')
        webhook = crawler.settings['SLACK_WEBHOOK']
        channel = crawler.settings['SLACK_CHANNEL']

        if not (webhook and channel):
            raise NotConfigured

        ext = cls(name, emoji, webhook, channel, crawler.stats)
        crawler.signals.connect(ext.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed,
                                signal=signals.spider_closed)
        crawler.signals.connect(ext.spider_error, signal=signals.spider_error)

        return ext

    def spider_opened(self, spider):
        title = 'Scraper {} started'.format(spider.name)

        payload = {
            'channel':
            self.channel,
            'username':
            self.name,
            'icon_emoji':
            self.emoji,
            'attachments': [{
                'title':
                title,
                'fallback':
                title,
                'color':
                'good',
                'author_name':
                socket.getfqdn(),
                'footer':
                self.name,
                'footer_icon':
                'https://scrapy.org/favicons/favicon-16x16.png',
                'ts':
                self.stats.get_value('start_time').replace(
                    tzinfo=timezone(timedelta(hours=0))).timestamp()
            }]
        }
        response = requests.post(self.webhook, json=payload)
        self._log_errors(spider, response)

    def spider_closed(self, spider, reason):
        title = 'Scraper {} finished'.format(spider.name)

        payload = {
            'channel':
            self.channel,
            'username':
            self.name,
            'icon_emoji':
            self.emoji,
            'attachments': [{
                'title':
                title,
                'fallback':
                title,
                'color':
                'good',
                'author_name':
                socket.getfqdn(),
                'fields': [{
                    'title': 'Reason',
                    'value': reason,
                    'short': True
                }, {
                    'title':
                    'Item Scraped Count',
                    'value':
                    self.stats.get_value('item_scraped_count') or 0,
                    'short':
                    True
                }, {
                    'title':
                    'Dropped items',
                    'value':
                    self.stats.get_value('item_dropped_count') or 0,
                    'short':
                    True
                }, {
                    'title':
                    'Invalid symbols',
                    'value':
                    self.stats.get_value('spider_exceptions/DropItem') or 0,
                    'short':
                    True
                }],
                'footer':
                self.name,
                'footer_icon':
                'https://scrapy.org/favicons/favicon-16x16.png',
                'ts':
                self.stats.get_value('finish_time').replace(
                    tzinfo=timezone(timedelta(hours=0))).timestamp()
            }]
        }
        response = requests.post(self.webhook, json=payload)
        self._log_errors(spider, response)

    def _log_errors(self, spider, response):
        if response.status_code != 200:
            msg = "Error connecting to Slack {}. Response is:\n{}".format(
                response.status_code, response.text)
            spider.logger.error(msg)
