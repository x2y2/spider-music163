# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import urllib2
import settings

class Music163Pipeline(object):
  def process_item(self, item, spider):
    dir_path = os.path.join(settings.MP3_STORE,spider.name)
    if not os.path.exists(dir_path):
      os.makedirs(dir_path)
    for url,title in zip(item['url'],item['title']):
      mp3_name = title + '.mp3'
      file_path = os.path.join(dir_path,mp3_name)
      if os.path.exists(file_path):
        continue
      else:
        os.mknod(file_path)
      with open(file_path,'wb') as fp:
        try:
          print 'start download {0}'.format(url)
          conn = urllib2.urlopen(url,timeout=3)
          fp.write(conn.read())
          print 'download {0} is end'.format(url)
        except Exception as e:
           print e
    return item
