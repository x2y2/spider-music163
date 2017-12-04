# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import urllib2
import settings
import threading

class Music163Pipeline(object):
  #item从spider中传递过来
  def process_item(self, item, spider):
    dir_path = os.path.join(settings.MP3_STORE,spider.name)
    if item is not None:
      for v in item['title']:
        for ptitle,values in v.items():
          for title,url,artist in zip(values['stitle'],values['surl'],values['artist']):  
            file_path = os.path.join(dir_path,ptitle)
            file_name = title + '-' + artist + '.mp3'
            #创建存储目录
            if not os.path.exists(file_path):
              os.makedirs(file_path)
            #避免重爬
            if os.path.exists(os.path.join(file_path,file_name)):
              continue
            else: 
              t = threading.Thread(target=self._download_songs,args=(file_path,file_name,url))
              t.start()
              t.join()

    return item

  def _download_songs(self,file_path,file_name,url):
    os.chdir(file_path)
    try:
      os.mknod(file_name)
      with open(os.path.join(file_path,file_name),'wb') as fp:
        try:
          print 'start download {0}'.format(file_name)
          conn = urllib2.urlopen(url,timeout=3)
          fp.write(conn.read())
          print 'finish download {0}'.format(file_name)
        except Exception as e:
           print e
    except Exception as e:
      print e

