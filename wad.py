#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib, json, sys, time
from collections import defaultdict

import config

########################################################################

def getPromotedFromPage(page, sort='all'):
  promoted = dict()
  
  url = config.API + '/links/promoted/page,' + str(page)
  if 'day' == sort or 'week' == sort or 'month' == sort:
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

def occurrencesByHours(dates):
  hours = defaultdict(int)
  
  for id in dates.keys():
    hours[time.strftime("%H", dates[id])] += 1
    
  return hours

########################################################################

promoted = getPromoted('day')
occurrences = occurrencesByHours(promoted)

for hour in sorted(occurrences.iterkeys()):
  print(hour + ': ' + str(occurrences[hour]))
