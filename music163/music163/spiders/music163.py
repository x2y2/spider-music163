#!/usr/bin/python
#encoding:utf-8 
import json
import os
import re
import base64
import requests
import time
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
from ..items import Music163Item
import urlparse



import scrapy
from scrapy.crawler import CrawlerProcess
class Music163Spider(scrapy.Spider):
  name = "music163"
  domain = "http://music.163.com"
  start_urls = ["http://music.163.com/#/discover/playlist"]

  def __init__(self):
    self.title = []

  def aesEncrypt(self,text,secKey):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey,2,'0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


  def rsaEncrypt(self,text,pubKey,modulus):
    text = text[::-1]
    rs = int(text.encode('hex'),16) ** int(pubKey,16) % int(modulus,16)
    return format(rs,'x').zfill(256)


  def createSecretKey(self,size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

  def __getUrl(self,id):
    url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
    text = {"ids": [id],"br":"128000",'csrf_token': 'e0f2e995baf3e1fc135a80ab8ee491ee'}
    headers = {'Cookie': 'appver=1.5.2;', 'Referer': 'http://music.163.com/'}
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'
    text = json.dumps(text)
    secKey = self.createSecretKey(16)
    encText = self.aesEncrypt(self.aesEncrypt(text, nonce), secKey)
    encSecKey = self.rsaEncrypt(secKey, pubKey, modulus)
    data = {'params': encText, 'encSecKey': encSecKey}
    req = requests.post(url,headers=headers, data=data)
    url = json.loads(req.text)['data'][0]['url']
    return url

  def __get_artist(self,soup,p_title):
    self.title[len(self.title) - 1][p_title]['artist'] = []
    artists = soup.find_all(name="div",attrs={'title':re.compile('.*'),'class':'text'})
    for each in artists:
      artist = each.span.get('title').encode('utf-8')
      self.title[len(self.title) - 1][p_title]['artist'].append(artist)
      print 'from {0} artist is {1}'.format(p_title,artist)

  def __get_songs_info(self,soup):
    playlist = soup.find_all(name="h2",attrs={'class': 'f-ff2 f-brk'})
    p_title = playlist[0].get_text().encode('utf-8')
    self.title.append({p_title:{}})
    self.__get_artist(soup,p_title)
    self.title[len(self.title) - 1][p_title]['surl'] = []
    self.title[len(self.title) - 1][p_title]['stitle'] = []
    songs = soup.find_all(name="span",attrs={'class': 'txt'})
    for each in songs:
      ids = each.a.get('href').split('=')[1]
      urls = self.__getUrl(ids)
      titles = each.b.get('title').encode('utf-8')
      self.title[len(self.title) - 1][p_title]['stitle'].append(titles)
      self.title[len(self.title) - 1][p_title]['surl'].append(urls)
      print 'song "{0}" from {1}'.format(titles,p_title)

  def playlist_parse(self,response):
    item = Music163Item()
    #title = []
    html = response.body
    soup = BeautifulSoup(html,'html.parser')
    #playlist = self.soup.find_all(name="h2",attrs={'class': 'f-ff2 f-brk'})
    #p_title = playlist[0].get_text().encode('utf-8')
    #self.title.append({p_title:{}})
    #self.title[len(title) - 1][p_title]['surl'] = []
    #self.title[len(title) - 1][p_title]['stitle'] = []
    #self.title[len(title) - 1][p_title]['artist'] = []
    #songs = soup.find_all(name="span",attrs={'class': 'txt'})
    #artists = soup.find_all(name="div",attrs={'title':re.compile('.*'),'class':'text'})
    #get artist
    #for each in artists:
    #  artist = each.span.get('title').encode('utf-8')
    #  self.title[len(title) - 1][p_title]['artist'].append(artist)
    #  print 'from {0} artist is {1}'.format(p_title,artist)
    #get song's info
    #for each in songs:
    #  ids = each.a.get('href').split('=')[1]
    #  urls = self.getUrl(ids)
    #  titles = each.b.get('title').encode('utf-8')
    #  self.title[len(title) - 1][p_title]['stitle'].append(titles)
    #  self.title[len(title) - 1][p_title]['surl'].append(urls)
    #  print 'song "{0}" from {1}'.format(titles,p_title)
    #self.__get_artist(soup)
    self.__get_songs_info(soup)
    item['title'] = self.title
    yield item

  def parse(self,response):
    html = response.body
    soup = BeautifulSoup(html,'html.parser')
    results = soup.find_all(name='a',attrs={'class': 'tit f-thide s-fc0'})
    #url = 'http://music.163.com/playlist?id=1982066521'
    #get playlist id
    for each in results:
      href = each.get('href')
      url = response.urljoin(href.encode('utf-8'))
      print 'seek out playlist [{0}]'.format(url)
      yield scrapy.Request(url = url,callback=self.playlist_parse)
    #pagedown
    next_page = soup.find_all(name='a',attrs={'class': 'zbtn znxt'})
    if next_page:
      next_url = next_page[0].get('href')
      url = response.urljoin(next_url.encode('utf-8'))
      yield scrapy.Request(url,callback=self.parse)

  



