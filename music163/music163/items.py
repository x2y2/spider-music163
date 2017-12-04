# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.item import Item,Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join

class Music163Item(scrapy.Item):
  # define the fields for your item here like:
  # name = scrapy.Field()
  title = scrapy.Field()

class Music163Loader(ItemLoader):
  default_item_class = Music163Item()
  default_input_processor = MapCompose(lambda s: s.strip())
  default_output_processor = TakeFirst()
  description_out = Join()
