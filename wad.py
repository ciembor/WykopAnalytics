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

def packOccurrences(occurrences, keys):
  promoted = []
  upcoming = []
  for key in keys:
    if key in occurrences['promoted'].keys():
      promoted.append(occurrences['promoted'][key])
    else:
      promoted.append(0);
    if key in occurrences['upcoming'].keys():
      upcoming.append(occurrences['upcoming'][key])
    else:
      upcoming.append(0);
  return {'keys': keys, 'promoted': promoted, 'upcoming': upcoming}
  
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def saveOccurrencesToFile(package, filename):
  output = 'response('
  output += json.dumps(package);
  output += ');'
  f = open(filename, 'w')
  f.write(output)
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

print("\n=> generowanie zestawień w formacie JSONP")
pack = {}

hour_occurrences = {'promoted': getOccurrences(promoted, 'hour'), 'upcoming': getOccurrences(upcoming, 'hour')}
hour_keys = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
             '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
             '20', '21', '22', '23']
pack['hour'] = packOccurrences(hour_occurrences, hour_keys)

day_occurrences = {'promoted': getOccurrences(promoted, 'day'), 'upcoming': getOccurrences(upcoming, 'day')}
day_keys = ['0', '1', '2', '3', '4', '5', '6']
pack['day'] = packOccurrences(day_occurrences, day_keys)

month_occurrences = {'promoted': getOccurrences(promoted, 'month'), 'upcoming': getOccurrences(upcoming, 'month')}
month_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
pack['month'] = packOccurrences(month_occurrences, month_keys)

saveOccurrencesToFile(pack, config.DIR + config.OUTPUT)
print("   wygenerowano zestawienia")

end = datetime.datetime.now()
print('\n=> aktualizacja trwała ' + str((end - begin).seconds) + ' sekund\n')
