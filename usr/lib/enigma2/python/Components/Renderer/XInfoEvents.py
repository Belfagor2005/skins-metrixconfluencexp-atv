# -*- coding: utf-8 -*-
# by digiteng...04.2020, 11.2020, 06.2021
# file by sunriser 07.2021

from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from enigma import eLabel, eTimer, eEPGCache, getBestPlayableServiceReference
from time import gmtime
import sys
import os
import re
import socket
import json
import requests

tmdb_api = "9273a48a3cbdcef9484bf45de6f53ff0"
omdb_api = "cb1d9f55"
epgcache = eEPGCache.getInstance()

if os.path.isdir("/tmp"):
        pathLoc = "/tmp/infos/"
else:
        pathLoc = "/tmp/infos/"
if not os.path.exists(pathLoc):
        os.mkdir(pathLoc)

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
                r'/.*|'
                r'\|\s[0-9]+\+|'
                r'[0-9]+\+|'
                r'\s\d{4}\Z|'
                r'([\(\[\|].*?[\)\]\|])|'
                r'(\"|\"\.|\"\,|\.)\s.+|'
                r'\"|\.|'
                r'Премьера\.\s|'
                r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
                r'(х|Х|м|М|т|Т|д|Д)/с\s|'
                r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
                r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
                r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
                r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
                r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)

class XInfoEvents(Renderer, VariableText):

        def __init__(self):
                Renderer.__init__(self)
                VariableText.__init__(self)
                self.intCheck()

        def intCheck(self):
                try:
                        socket.setdefaulttimeout(1)
                        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
                        return True
                except:
                        return False

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
                                self.downloadInfos(eventNm)

                        if os.path.exists(infos_file):
                                with open(infos_file) as f:
                                        data = json.load(f)

                                        Title = data["Title"]
                                        imdbRating = data["imdbRating"]
                                        Country = data["Country"]
                                        Year = data["Year"]
                                        Rated = data["Rated"]
                                        Genre = data["Genre"]
                                        Awards = data["Awards"]
                                        Director = data["Director"]
                                        Writer = data["Writer"]
                                        Actors = data["Actors"]

                                        if Title != "N/A" or Title != "":
                                                self.text = "Nome: %s\nAnno: %s\nNazione: %s\nValutazione imdb: %s\nQualifica di età: %s\ngenere: %s\nPremi: %s\nDirettore: %s\nScenario: %s\nattori: %s" % (str(Title),str(Year),str(Country),str(imdbRating),str(Rated),str(Genre),str(Awards),str(Director),str(Writer),str(Actors))
                                        else:
                                                self.text = None
                else:
                        self.text = None

        def downloadInfos(self, eventNm):
                self.year = self.filterSearch()
                try:
                        url_tmdb = "http://api.tmdb.org/3/search/{}?api_key={}&query={}".format(self.srch, tmdb_api, quote(eventNm))
                        if self.year != None:
                                url_tmdb += "&year={}".format(self.year)
                                try:
                                        title = json.load(urlopen(url_tmdb))["results"][0]["title"]
                                except:
                                        title = json.load(urlopen(url_tmdb))["results"][0]["original_name"]
                                url_omdb = "http://www.omdbapi.com/?apikey={}&t={}".format(omdb_api, quote(title))
                                data_omdb = json.load(urlopen(url_omdb))
                                if(data_omdb["Plot"]):
                                        dwn_infos = "{}{}.json".format(pathLoc, eventNm)
                                        open(dwn_infos,"w").write(json.dumps(data_omdb))
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
                        yr = [ _y for _y in re.findall(r'\d{4}', sd) if '1930' <= _y <= '%s' % gmtime().tm_year ]
                        return '%s' % yr[-1] if yr else ''
                except:
                        pass

        def epgs(self):
                events = None
                import NavigationInstance
                ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
                events = epgcache.lookupEvent(['IBDCT', (ref, 0, -1, -1)])
                for i in range(9):
                        titleNxt = events[i][4]
                        eventNm = REGEX.sub('', titleNxt).rstrip().replace('ё','е')
                        infos_file = "{}{}.json".format(pathLoc, eventNm)
                        if not os.path.exists(infos_file):
                                self.downloadInfos(eventNm)
                return

        def delay2(self):
                self.timer = eTimer()
                self.timer.callback.append(self.dwn)
                self.timer.start(2000, True)

        def dwn(self):
                start_new_thread(self.epgs, ())
