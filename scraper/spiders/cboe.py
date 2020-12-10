# -*- coding: utf-8 -*-

from datetime import date, datetime
import os

import pandas as pd
import scrapy
from scrapy.exceptions import DropItem
from scrapy.loader import ItemLoader
from scrapy.http import Request

from scraper import utils
from scraper.items import DataItem


class CBOESpider(scrapy.Spider):
    name = 'cboe'
    allowed_domains = ['cboe.com']
    spider_path = utils.create_spider_path(name)
    api_endpoint = 'https://cdn.cboe.com/api/global/delayed_quotes/options/'

    custom_settings = {
        'ITEM_PIPELINES': {
            'scraper.pipelines.CompressAndSavePipeline': 200
        },
        'SPIDER_DATA_PATH':
        spider_path,
        'FEED_URI':
        os.path.join(
            spider_path, 'cboe_feed',
            '{}_feed_{}.csv'.format(name,
                                    datetime.now().strftime('%Y%m%d%H%M%S')))
    }

    def __init__(self, *args, **kwargs):
        super(CBOESpider, self).__init__(*args, **kwargs)

        if 'SYMBOLS_FILE_PATH' in os.environ:
            symbols_file = os.environ['SYMBOLS_FILE_PATH']
            with open(symbols_file, 'r') as f:
                self.symbols = [symbol.rstrip('\n').upper() for symbol in f]
        else:
            self.symbols = CBOESpider._get_all_listed_symbols()

    def start_requests(self):
        for symbol in self.symbols:
            loader = ItemLoader(item=DataItem())
            loader.add_value('symbol', symbol)
            loader.add_value('symbol_path', symbol + '_daily')
            loader.add_value('start_date', datetime.now().isoformat())
            loader.add_value(
                'filename',
                symbol + '_' + date.today().strftime('%Y%m%d') + '.json')

            request_url = "{endpoint}{symbol}.json".format(
                endpoint=CBOESpider.api_endpoint, symbol=symbol)

            yield Request(request_url,
                          callback=self.fetch_data,
                          meta={'loader': loader})

    def fetch_data(self, response):
        loader = response.meta['loader']

        content_type = response.headers.get('Content-Type')
        if not content_type.startswith(b'application/json'):
            symbol, = loader.get_collected_values('symbol')
            raise DropItem('Error downloading data for {}'.format(symbol))

        loader.add_value('end_date', datetime.now().isoformat())
        loader.add_value('data', response.body)

        return loader.load_item()

    def _get_all_listed_symbols():
        """Returns array of all listed symbols.
        https://markets.cboe.com/us/options/symboldir/equity_index_options/
        """
        url = 'https://markets.cboe.com/us/options/symboldir/equity_index_options/?download=csv'
        symbols_df = pd.read_csv(url)
        return symbols_df.iloc[:, 1].array
