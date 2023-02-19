# -*- coding: utf-8 -*-
# by digiteng...04.2020, 11.2020, 06.2021
# file by sunriser 07.2021
# <widget source="session.Event_Now" render="ZInfoEvents"/>
# <widget source="session.Event_Next" render="ZInfoEvents"/>
# <widget source="Event" render="ZInfoEvents"/>
#edit by lululla 07.2022
from __future__ import print_function
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from Components.config import config
from enigma import eLabel, eTimer, eEPGCache#, getBestPlayableServiceReference
from time import gmtime
import glob
import json
import os
import re
import requests
import shutil
import socket
import sys
import NavigationInstance
global cur_skin, my_cur_skin, tmdb_api, omdb_api
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
epgcache = eEPGCache.getInstance()
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')

if os.path.isdir("/tmp"):
        pathLoc = "/tmp/infos/"
else:
        pathLoc = "/tmp/infos/"
if not os.path.exists(pathLoc):
        os.mkdir(pathLoc)

try:
    if my_cur_skin == False:
        myz_skin = "/usr/share/enigma2/%s/apikey" %cur_skin
        print('skinz namez', myz_skin)
        omdb_skin = "/usr/share/enigma2/%s/omdbkey" %cur_skin
        print('skinz namez', omdb_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                tmdb_api = f.read()
        if os.path.exists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
except:
    my_cur_skin = False

PY3 = (sys.version_info[0] == 3)

if PY3:
    from urllib.parse import quote, urlencode
    from urllib.request import urlopen, Request
    from _thread import start_new_thread
else:
    from urllib import quote, urlencode
    from urllib2 import urlopen, Request
    from thread import start_new_thread

REGEX = re.compile(
        r'([\(\[]).*?([\)\]])|'
        r'(: odc.\d+)|'
        r'(\d+: odc.\d+)|'
        r'(\d+ odc.\d+)|(:)|'
        r'( -(.*?).*)|(,)|'
        r'!|'
        r'/.*|'
        r'\|\s[0-9]+\+|'
        r'[0-9]+\+|'
        r'\s\d{4}\Z|'
        r'([\(\[\|].*?[\)\]\|])|'
        r'(\"|\"\.|\"\,|\.)\s.+|'
        r'\"|:|'
        r'Премьера\.\s|'
        r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
        r'(х|Х|м|М|т|Т|д|Д)/с\s|'
        r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
        r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
        r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)


def intCheck():
    import socket
    try:
        response = urlopen("http://google.com", None, 5)
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True


class xInfoEvents(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        adsl = intCheck()
        if not adsl:
            return
        VariableText.__init__(self)

    GUI_WIDGET = eLabel

    def changed(self, what):
        try:
            if what[0] == self.CHANGED_CLEAR:
                self.text = ""
            if what[0] != self.CHANGED_CLEAR:
                self.showInfos()
        except:
            pass

    def showInfos(self):
        self.event = self.source.event
        if self.event:
            self.delay2()
            eventNm = REGEX.sub("", self.event.getEventName()).strip().replace('ё','е')
            infos_file = "{}{}.json".format(pathLoc, eventNm)
            if not os.path.exists(infos_file):
                self.downloadInfos(eventNm, infos_file)
            # else:
            if os.path.exists(infos_file):
                try:
                    with open(infos_file) as f:
                        data = json.load(f)
                        Title =''
                        imdbRating = ''
                        Country = ''
                        Year = ''
                        Rated = ''
                        Genre = ''
                        Awards = ''
                        Director = ''
                        Writer = ''
                        Actors = ''
                        if 'Title' in data:
                            Title = data["Title"]
                        if 'imdbrating' in data:
                            imdbRating = data["imdbRating"]
                        if 'country' in data:
                            Country = data["Country"]
                        if 'year' in data:
                            Year = data["Year"]
                        if 'rated' in data:                        
                            Rated = data["Rated"]
                        if 'genre' in data:                        
                            Genre = data["Genre"]
                        if 'awards' in data: 
                            Awards = data["Awards"]
                        if 'director' in data: 
                            Director = data["Director"]
                        if 'writer' in data: 
                            Writer = data["Writer"]
                        if 'actors' in data:     
                            Actors = data["Actors"]

                        if Title and Title != "N/A":
                            with open("/tmp/rating", "w") as f:
                                f.write("%s\n%s" % (imdbRating, Rated))
                            self.text = "Title : %s" % str(Title)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nYear : %s" % str(Year)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nCountry : %s" % str(Country)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nGenre : %s" % str(Genre)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nDirector : %s" % str(Director)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nAwards : %s" % str(Awards)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nWriter : %s" % str(Writer)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nCast : %s" % str(Actors)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nRated : %s" % str(Rated)  # .encode('utf-8').decode('utf-8')
                            self.text += "\nImdb : %s" % str(imdbRating)  # .encode('utf-8').decode('utf-8')
                            print("text= ", self.text)
                            self.text = "Anno: %s\nNazione: %s\nGenere: %s\nRegista: %s\nAttori: %s" % (str(Year), str(Country), str(Genre), str(Director), str(Actors))

                        else:
                            if os.path.exists("/tmp/rating"):
                                os.remove("/tmp/rating")
                                print('/tmp/rating removed')
                                self.text = None
                            return self.text
                except Exception as e:
                    print(e)
            else:
                self.text = None

    def downloadInfos(self, eventNm, infos_file):
        self.year = self.filterSearch()
        try:
            try:
                url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(self.srch, tmdb_api, quote(eventNm))
                if self.year != None:
                    url_tmdb += "&year={}".format(self.year)
                    print('url_tmdb1: ', url_tmdb)
                try:
                    title = json.load(urlopen(url_tmdb))["results"][0]["title"]
                except:
                    title = json.load(urlopen(url_tmdb))["results"][0]["original_name"]
                print('Title1: ', title)
            except:
                pass
            # {
                # "Title": "CSI: Miami",
                # "Year": "2002–2012",
                # "Rated": "TV-14",
                # "Released": "23 Sep 2002",
                # "Runtime": "43 min",
                # "Genre": "Action, Crime, Drama",
                # "Director": "N/A",
                # "Writer": "Ann Donahue, Carol Mendelsohn, Anthony E. Zuiker",
                # "Actors": "David Caruso, Emily Procter, Adam Rodriguez",
                # "Plot": "The cases of the Miami-Dade, Florida police department's Crime Scene Investigations unit.",
                # "Language": "English, Spanish, Greek",
                # "Country": "United States",
                # "Awards": "Won 2 Primetime Emmys. 28 wins & 44 nominations total",
                # "Poster": "https://m.media-amazon.com/images/M/MV5BOTU3ZTI5ZGEtYjhiMy00ODU4LTgyM2UtNDhlYjBhMjc4MjIwXkEyXkFqcGdeQXVyMTYzMDM0NTU@._V1_SX300.jpg",
                # "Ratings": [
                    # {
                        # "Source": "Internet Movie Database",
                        # "Value": "6.4/10"
                    # }
                # ],
                # "Metascore": "N/A",
                # "imdbRating": "6.4",
                # "imdbVotes": "56,990",
                # "imdbID": "tt0313043",
                # "Type": "series",
                # "totalSeasons": "10",
                # "Response": "True"
            # }

            ###### for future
            # Title=None
            # Type = None
            # Genre = None
            # Language = None
            # Country = None
            # imdbRating = None
            # imdbID = None
            # Rated = None
            # Duration = None
            # Year = None
            # Released=None
            # Director = None
            # Writer = None
            # Actors = None
            # Awards=None
            # Plot = ""
            # Description = None
            # Rating = ""

            # url_tmdb += "&year={}".format(self.year)
            # try:
                    # title = json.load(urlopen(url_tmdb))["results"][0]["title"]
            # except:
                    # title = json.load(urlopen(url_tmdb))["results"][0]["original_title"]

            # try:
                # for omdb_api in omdb_api:

                    # url_omdb = "http://www.omdbapi.com/?apikey={}&t={}".format(omdb_api, quote(title))
                    # data_omdb = json.load(urlopen(url_omdb))
                    # if(data_omdb["Plot"]):
                            # dwn_infos = "{}{}.json".format(pathLoc, eventNm)
                            # open(dwn_infos,"w").write(json.dumps(data_omdb))
            # except:
                # pass
            # omdb_api = "6a4c9432"

            try:
                url_omdb = "http://www.omdbapi.com/?apikey={}&t={}".format(omdb_api, quote(title))
                print('data_omdb ', url_omdb)
                data_omdb = json.load(urlopen(url_omdb))
                print('data_omdb ', data_omdb)
                # if(data_omdb["Plot"]):
                dwn_infos = "{}{}.json".format(pathLoc, eventNm)
                open(dwn_infos, "w").write(json.dumps(data_omdb))
            except:
                pass
        except Exception as e:
            print('error ', str(e))
            # url_ggl = "https://www.google.it/search?q={}+imdb".format(quote(eventNm))
            # if self.year != None:
                    # url_ggl += "+{}".format(self.year)
                    # fl = requests.get(url_ggl).text
                    # ptrn = "https://www.imdb.com/title/(tt\d*)"
                    # res = re.search(ptrn, fl)
                    # imdb_id  = res.group(1)
                    # url_omdb = "http://www.omdbapi.com/?apikey={}&i={}".format(omdb_api, quote(imdb_id))
                    # data_omdb = json.load(urlopen(url_omdb))
                    # if(data_omdb["Plot"]):
                            # dwn_infos = "{}{}.json".format(pathLoc, eventNm)
                            # open(dwn_infos,"w").write(json.dumps(data_omdb))

    def filterSearch(self):
        try:
            sd = "%s\n%s\n%s" % (self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
            w = [
                    "t/s",
                    "Т/s",
                    "SM",
                    "SM",
                    "d/s",
                    "D/s",
                    "stagione",
                    "Sig.",
                    "episodio",
                    "serie TV",
                    "serie"
                    ]
            for i in w:
                if i in sd:
                    self.srch = "tv"
                    break
                else:
                    self.srch = "multi"
            yr = [_y for _y in re.findall(r'\d{4}', sd) if '1930' <= _y <= '%s' % gmtime().tm_year]
            return '%s' % yr[-1] if yr else None
        except:
            pass

    def epgs(self):
        try:
            events = None
            # import NavigationInstance
            ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
            events = epgcache.lookupEvent(['IBDCT', (ref, 0, -1, -1)])
            for i in range(9):
                titleNxt = events[i][4]
                eventNm = REGEX.sub('', titleNxt).rstrip().replace('ё','е')
                infos_file = "{}{}.json".format(pathLoc, eventNm)
                if not os.path.exists(infos_file):
                    self.downloadInfos(eventNm, infos_file)
        except:
            pass

    def delay2(self):
        self.timer = eTimer()
        self.timer.callback.append(self.dwn)
        self.timer.start(50, True)

    def dwn(self):
        start_new_thread(self.epgs, ())
