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

def getPromotedFromPage(page, sort='all', current_promoted={}):
  promoted = dict()
  
  url = config.API + '/links/promoted/page,' + str(page)
  if sort in ('day', 'week', 'month'):
    url += ',sort,' + sort
  url += ',' + config.KEY
  
  sys.stdout.write('   pobieram ' + str(page) + ' stronę... ')
  for link in json.load(urllib.urlopen(url)):
    if not (int(link['id']) in current_promoted.keys()):
      promoted[link['id']] = time.strptime(link['date'], "%Y-%m-%d %H:%M:%S")
  print("ok!");
  
  return promoted
  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getPromoted(sort='all', current_promoted={}):
  promoted = dict()
  i = 1
  while True:
    page = getPromotedFromPage(i, sort, current_promoted)
    #if not page:
    #  break
    promoted.update(page)
    if len(page) < 25:
      break
    i += 1
  print('   pobrano ' + str(len(promoted)) + ' nowych znalezisk')
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

def saveOccurrencesToFile(occurrences, filename):
  keys = sorted(occurrences['promoted'].keys())
  promoted = []
  upcoming = []
  for key in keys:
    promoted.append(occurrences['promoted'][key])
    upcoming.append(occurrences['upcoming'][key])
  json_dump = json.dumps({'keys': keys, 'promoted': promoted, 'upcoming': upcoming})
  f = open(filename, 'w')
  f.write(json_dump)
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
  print('   pobrano ' + str(len(upcoming)) + ' nowych znalezisk')
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

begin = datetime.datetime.now()
print('\n==> ' + begin.strftime('%Y-%m-%d %H:%M:%S') + ' <==')

# pobierz znaleziska ze strony głównej
print("\n=> strona główna")
promoted = getLinksFromFile(config.DIR + config.PROMOTED)
print("   wczytano " + str(len(promoted)) + " znalezisk z historii")
new_promoted = getPromoted('day', promoted)

# pobierz znaleziska z wykopaliska
print("\n=> wykopalisko")
upcoming = getLinksFromFile(config.DIR + config.UPCOMING)
print("   wczytano " + str(len(upcoming)) + " znalezisk z historii")
new_upcoming = getUpcoming('date', max(upcoming.keys(), key=int))

# dodaj pobrane znaleziska do obecnych znalezisk
for key in new_promoted.keys():
  promoted[key] = new_promoted[key]  
for key in new_upcoming.keys():
  upcoming[key] = new_upcoming[key]

# usuń z wykopaliska te znaleziska, które trafiły w międzyczasie na stronę główną
for key in promoted:
  if key in upcoming.keys():
    del upcoming[key]

# zapisz znaleziska do plików
saveLinksToFile(promoted, config.DIR + config.PROMOTED)
saveLinksToFile(upcoming, config.DIR + config.UPCOMING)

print("\n=> generowanie zestawień w formacie JSON")

promoted_occurrences = getOccurrences(promoted, 'hour')
upcoming_occurrences = getOccurrences(upcoming, 'hour')
saveOccurrencesToFile({'upcoming': upcoming_occurrences, 
                       'promoted': promoted_occurrences},
                       config.DIR + config.HOUR)
print("   wygenerowano zestawienie godzinne")

promoted_occurrences = getOccurrences(promoted, 'day')
upcoming_occurrences = getOccurrences(upcoming, 'day')
saveOccurrencesToFile({'upcoming': upcoming_occurrences, 
                       'promoted': promoted_occurrences},
                       config.DIR + config.DAY)
print("   wygenerowano zestawienie dzienne")

promoted_occurrences = getOccurrences(promoted, 'month')
upcoming_occurrences = getOccurrences(upcoming, 'month')
saveOccurrencesToFile({'upcoming': upcoming_occurrences, 
                       'promoted': promoted_occurrences},
                       config.DIR + config.MONTH)
print("   wygenerowano zestawienie miesięczne")

end = datetime.datetime.now()
print('\n=> aktualizacja trwała ' + str((end - begin).seconds) + ' sekund\n')
