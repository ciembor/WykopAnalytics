#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import time
import datetime

import urllib
import json

from collections import defaultdict

import config

########################################################################

def getPromotedFromPage(page, sort='all'):
  promoted = dict()
  
  url = config.API + '/links/promoted/page,' + str(page)
  if sort in ('day', 'week', 'month'):
    url += ',sort,' + sort
  url += ',' + config.KEY
  
  sys.stdout.write('pobieram ' + str(page) + ' stronę... ')
  for link in json.load(urllib.urlopen(url)):
    promoted[link['id']] = time.strptime(link['date'], "%Y-%m-%d %H:%M:%S")
  print("ok!");
  
  return promoted
  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getPromoted(sort='all'):
  promoted = dict()
  i = 1
  
  while True:
    page = getPromotedFromPage(i, sort)
    if not page:
      break
    promoted.update(page)
    i += 1
    
  return promoted

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getOccurrences(dates, sort):
  occurrences = defaultdict(int)
  sorts = {'hour': '%H', 'day': '%w', 'month': '%m'}
  
  if sort in sorts.keys():
    for ident in dates.keys():
      occurrences[time.strftime(sorts[sort], dates[ident])] += 1
    
  return occurrences

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getLastId():
  url = config.API + '/links/upcoming/sort,date'
  url += ',' + config.KEY
  return json.load(urllib.urlopen(url))[0]['id']

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getLinks(firstId, lastId): 
  links = dict()
  
  # test
  begin = datetime.datetime.now()
  
  for ident in range(firstId, lastId + 1):
    url = config.API + '/link/index/' + str(ident)
    url += '/' + config.KEY
    link = json.load(urllib.urlopen(url))
    if not 'error' in link.keys():
      links[link['id']] = time.strptime(link['date'], "%Y-%m-%d %H:%M:%S")
  
  # test
  end = datetime.datetime.now()
  print(str((end - begin).seconds) + ' seconds')
  
  return links

########################################################################

"""
promoted = getPromoted('week')
occurrences = getOccurrences(promoted, 'day')

for key in sorted(occurrences.iterkeys()):
  print(key + ': ' + str(occurrences[key]))
"""

ident = getLastId()
links = getLinks(ident - 100, ident)

print(len(links))

for key in links.keys():
  print(str(key) + ':' + str(int(time.mktime(links[key]))))
