#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import imp
import time
import datetime

import urllib
import json

from collections import defaultdict
from optparse import OptionParser

########################################################################

# pobranie argumentów programu
parser = OptionParser()
parser.add_option("-c", "--config", dest="config",
                  help=u"ścieżka do pliku konfiguracyjnego", metavar="PLIK")
parser.add_option("-d", "--database", dest="database",
                  help=u"ścieżka do katalogu przechowującego pliki z danymi", metavar="KATALOG")
parser.add_option("-a", "--appkey", dest="appkey",
                  help=u"klucz do API serwisu wykop.pl")
(options, args) = parser.parse_args()

# walidacja konfiguracji
try: 
  if options.config:
    config = imp.load_source('config', options.config)
  else:
    import config
except Exception:
  print("błąd: nie można załadować pliku konfiguracyjnego!")
  sys.exit(1)

if options.appkey:
  config.KEY = options.appkey
  
if not config.KEY or config.KEY == '':
  print("błąd: brak klucza do API (http://www.wykop.pl/developers/appnew/)")
  sys.exit(1)
else:
  config.KEY = "appkey," + config.KEY

if options.database:
  config.DIR = options.database

if config.DIR[-1] != '/':
  config.DIR = config.DIR + '/'

if not os.path.isdir(config.DIR):
  try: 
    os.mkdir(config.DIR)
    print("=> stworzono katalog dla bazy danych")
  except Exception:
    print("błąd: nie można utworzyć katalogu dla bazy danych!")
    sys.exit(1)
    
if not (os.access(config.DIR, os.W_OK) or os.access(config.DIR, os.R_OK)):
  print("błąd: brak praw do zapisu lub odczytu w katalogu z bazą danych!")
  sys.exit(1)


########################################################################

def getPromotedFromPage(page, sort='all', current_promoted={}):
  promoted = dict()
  
  url = config.API + '/links/promoted/page,' + str(page)
  if sort in ('day', 'week', 'month'):
    url += ',sort,' + sort
  url += ',' + config.KEY
  
  sys.stdout.write('   pobieram ' + str(page) + ' stronę... ')
  
  try:
    for link in json.load(urllib.urlopen(url)):
      if not (int(link['id']) in current_promoted.keys()):
        promoted[link['id']] = time.strptime(link['date'], "%Y-%m-%d %H:%M:%S")
    print("ok!");
  except Exception:
    print("\n   błąd: nie można pobrać danych z serwera!")
    sys.exit(1)

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
    try:
      return json.load(urllib.urlopen(url))[0]['id']
    except Exception:
      print("\n   błąd: nie można pobrać danych z serwera!")
      sys.exit(1)
  else:
    print('error!')

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  

def getLinks(firstId, lastId): 
  links = dict()

  for ident in range(firstId, lastId + 1):
    url = config.API + '/link/index/' + str(ident)
    url += '/' + config.KEY
    
    try:
      link = json.load(urllib.urlopen(url))
    except Exception:
      print("\n   błąd: nie można pobrać danych z serwera!")
      sys.exit(1)
      
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
  
  try:
    for link in json.load(urllib.urlopen(url)):
      if int(link['id']) == last_id:
        break
      upcoming[link['id']] = time.strptime(link['date'], "%Y-%m-%d %H:%M:%S")
    print("ok!");
  except Exception:
    print("\n   błąd: nie można pobrać danych z serwera!")
    sys.exit(1)

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
  if os.path.isfile(filename):
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
  else:
    return {}

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
try:
  maximum = max(upcoming.keys(), key=int) 
except Exception:
  maximum = 0
new_upcoming = getUpcoming('date', maximum)

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

# generuj dzienne zestawienie ilości znalezisk (okno godzinne)
hour_occurrences = {'promoted': getOccurrences(promoted, 'hour'), 
                    'upcoming': getOccurrences(upcoming, 'hour')}
hour_keys = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
             '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
             '20', '21', '22', '23']
pack['hour'] = packOccurrences(hour_occurrences, hour_keys)

# generuj tygodniowe zestawienie ilości znalezik (okno dzienne)
day_occurrences = {'promoted': getOccurrences(promoted, 'day'), 
                   'upcoming': getOccurrences(upcoming, 'day')}
day_keys = ['0', '1', '2', '3', '4', '5', '6']
pack['day'] = packOccurrences(day_occurrences, day_keys)

# generuj roczne zestawienie ilości znalezisk (okno miesięczne)
month_occurrences = {'promoted': getOccurrences(promoted, 'month'), 
                     'upcoming': getOccurrences(upcoming, 'month')}
month_keys = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
pack['month'] = packOccurrences(month_occurrences, month_keys)

# zapisz zestawienia do pliku
saveOccurrencesToFile(pack, config.DIR + config.OUTPUT)
print("   wygenerowano zestawienia")

end = datetime.datetime.now()
print('\n=> aktualizacja trwała ' + str((end - begin).seconds) + ' sekund\n')

