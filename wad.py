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

def getPromotedFromPage(page, sort='all', last_id=0):
  promoted = dict()
  
  url = config.API + '/links/promoted/page,' + str(page)
  if sort in ('day', 'week', 'month'):
    url += ',sort,' + sort
  url += ',' + config.KEY
  
  sys.stdout.write('   pobieram ' + str(page) + ' stronę... ')
  for link in json.load(urllib.urlopen(url)):
    if int(link['id']) == last_id:
      break
    promoted[link['id']] = time.strptime(link['date'], "%Y-%m-%d %H:%M:%S")
  print("ok!");
  
  return promoted
  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getPromoted(sort='all', last_id=0):
  promoted = dict()
  i = 1
  while True:
    page = getPromotedFromPage(i, sort, last_id)
    #if not page:
    #  break
    promoted.update(page)
    if len(page) < 25:
      break
    i += 1
  print('   pobrano ' + str(i-1) + ' nowych znalezisk')
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
  if not 'error' in link.keys():
    return json.load(urllib.urlopen(url))[0]['id']
  else:
    print('error!')

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getLinks(firstId, lastId): 
  links = dict()

  for ident in range(firstId, lastId + 1):
    url = config.API + '/link/index/' + str(ident)
    url += '/' + config.KEY
    link = json.load(urllib.urlopen(url))
    if not 'error' in link.keys():
      links[link['id']] = time.strptime(link['date'], "%Y-%m-%d %H:%M:%S")

  return links

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def saveLinksToFile(links, filename, sort='save'):
  sorts = {'save': 'w', 'append': 'a'}
  
  if sort in sorts.keys():
    f = open(filename, sorts[sort])
    for key in links.keys():
      f.write(str(key) + ':' + str(int(time.mktime(links[key]))) + '\n')
    f.close()
  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getUpcomingFromPage(page, sort='date', last_id=0):
  upcoming = dict()
  
  url = config.API + '/links/upcoming/page,' + str(page)
  if sort in ('date', 'votes', 'comments'):
    url += ',sort,' + sort
  url += ',' + config.KEY

  sys.stdout.write('   pobieram ' + str(page) + ' stronę... ')
  for link in json.load(urllib.urlopen(url)):
    if int(link['id']) == last_id:
      break
    upcoming[link['id']] = time.strptime(link['date'], "%Y-%m-%d %H:%M:%S")
  print("ok!");
  
  return upcoming
  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getUpcoming(sort='date', last_id=0):
  upcoming = dict()
  i = 1
  
  while True:
    page = getUpcomingFromPage(i, sort, last_id)
    #if not page:
    #  break
    upcoming.update(page)
    if len(page) < 25:
      break
    i += 1
  print('   pobrano ' + str(i-1) + ' nowych znalezisk')
  return upcoming

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getLinksFromFile(filename):
  links = dict()
  f = open(filename, 'r')
  i = 0
  for line in f:
    record = line.split(':')
    if 2 == len(record):
      links[int(record[0])] = time.localtime(int(record[1]))
    else:
      print("uwaga: nie udało się odczytać " + str(i) + " linii z pliku " + filename)
    i += 1
  f.close()
  return links

########################################################################

# test
begin = datetime.datetime.now()

print('\n==> ' + begin.strftime('%Y-%m-%d %H:%M:%S') + ' <==')

print("\n=> strona główna")
promoted = getLinksFromFile(config.DIR + config.PROMOTED)
print("   wczytano " + str(len(promoted)) + " znalezisk z historii")
new_promoted = getPromoted('day', max(promoted.keys(), key=int))

print("\n=> wykopalisko")
upcoming = getLinksFromFile(config.DIR + config.UPCOMING)
print("   wczytano " + str(len(upcoming)) + " znalezisk z historii")
new_upcoming = getUpcoming('date', max(upcoming.keys(), key=int))

for key in new_promoted.keys():
  promoted[key] = new_promoted[key]
  
for key in new_upcoming.keys():
  upcoming[key] = new_upcoming[key]

# usuń z wykopaliska te znaleziska, które trafiły na stronę główną
for key in promoted:
  if key in upcoming.keys():
    del upcoming[key]

saveLinksToFile(promoted, config.DIR + config.PROMOTED)
saveLinksToFile(upcoming, config.DIR + config.UPCOMING)

end = datetime.datetime.now()
print('\n=> aktualizacja trwała ' + str((end - begin).seconds) + ' sekund\n')
