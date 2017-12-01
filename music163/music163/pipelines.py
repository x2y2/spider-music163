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
    for v in item['title']:
      for ptitle,values in v.items():
        for title,url,artist in zip(values['stitle'],values['surl'],values['artist']):  
          file_path = os.path.join(dir_path,ptitle)
          file_name = title + '-' + artist + '.mp3'
          if not os.path.exists(file_path):
            os.makedirs(file_path)
          if os.path.exists(os.path.join(file_path,file_name)):
            continue
          else: 
            os.chdir(file_path)
            try:
              os.mknod(file_name)
              with open(os.path.join(file_path,file_name),'wb') as fp:
                try:
                  print 'start download {0}'.format(url)
                  conn = urllib2.urlopen(url,timeout=3)
                  fp.write(conn.read())
                  print 'finish download {0}'.format(url)
                except Exception as e:
                   print e
            except Exception as e:
              print e
    return item

