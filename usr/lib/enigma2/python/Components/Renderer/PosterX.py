#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021,
# 08.2021(stb lang support),
# 09.2021 mini fixes
# 06.2022 add api key from apikey file in folder skin [lululla]
# © Provided that digiteng rights are protected, all or part of the code can be used, modified...
# © Provided that digiteng rights are protected, all or part of the code can be used, modified...
# russian and py3 support by sunriser...
# downloading in the background while zaping...
# by beber...03.2022,
# 03.2022 several enhancements : several renders with one queue thread, google search (incl. molotov for france) + autosearch & autoclean thread ...
#
# for infobar,
# <widget source="session.Event_Now" render="PosterX" position="100,100" size="185,278" />
# <widget source="session.Event_Next" render="PosterX" position="100,100" size="100,150" />
# <widget source="session.Event_Now" render="PosterX" position="100,100" size="185,278" nexts="2" />
# <widget source="session.CurrentService" render="PosterX" position="100,100" size="185,278" nexts="3" />
# for ch,
# <widget source="ServiceEvent" render="PosterX" position="100,100" size="185,278" />
# <widget source="ServiceEvent" render="PosterX" position="100,100" size="185,278" nexts="2" />
# for epg, event
# <widget source="Event" render="PosterX" position="100,100" size="185,278" />
# <widget source="Event" render="PosterX" position="100,100" size="185,278" nexts="2" />
#============
# for infobar,
# <widget source="session.Event_Now" render="PosterX" position="0,125" size="185,278" path="/media/hdd/poster/" nexts="10" language="en" zPosition="9" />
# for ch,
# <widget source="ServiceEvent" render="PosterX" position="820,100" size="100,150" path="/media/hdd/poster/" zPosition="9" />
# for secondInfobar,
# <widget source="session.Event_Now" render="PosterX" position="20,155" size="100,150" path="/media/hdd/poster/" zPosition="9" />
# <widget source="session.Event_Next" render="PosterX" position="1080,155" size="100,150" path="/media/hdd/poster/" zPosition="9" />
# for epg, event
# <widget source="Event" render="PosterX" position="931,184" size="185,278" path="/media/hdd/poster/" zPosition="9" />
 
from __future__ import absolute_import
from __future__ import print_function
from Components.Renderer.Renderer import Renderer
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from ServiceReference import ServiceReference
from enigma import ePixmap, eTimer, loadJPG, eEPGCache
import NavigationInstance
import json
import os
import re
import socket
import sys
try:
    from Components.config import config
    lng = config.osd.language.value

except:
    lng = None
    pass

tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
epgcache = eEPGCache.getInstance()
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')

try:
    if my_cur_skin == False:
        myz_skin = "/usr/share/enigma2/%s/apikey" %cur_skin
        print('skinz namez', myz_skin)
        if os.path.exists(myz_skin):
            with open(myz_skin, "r") as f:
                tmdb_api = f.read()
                my_cur_skin = True
except:
    my_cur_skin = False

PY3 = (sys.version_info[0] == 3)
try:
    if PY3:
        from urllib.parse import quote
        from urllib.request import urlopen
        from _thread import start_new_thread
    else:
        from urllib2 import urlopen, quote
        from thread import start_new_thread
except:
    pass


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


class PosterX(Renderer):

    GUI_WIDGET = ePixmap

    def __init__(self):
        Renderer.__init__(self)
        self.path = "/tmp/poster/"
        self.language = None
        self.size = "185"
        self.nexts = 1
        self.downloading = False
        if not self.intCheck():
            return

        self.timer = eTimer()

        try:
            self.timer.callback.append(self.getEventData)
        except:
            self.timer_conn = self.timerimage.timeout.connect(self.getEventData)
            
    def applySkin(self, desktop, parent):
            attribs = []
            for (attrib, value,) in self.skinAttributes:
                    if attrib == "nexts":
                            self.nxts = int(value)
                    attribs.append((attrib, value))
            self.skinAttributes = attribs
            return Renderer.applySkin(self, desktop, parent)

    # def applySkin(self, desktop, parent):
        # if self.skinAttributes:
            # for (attrib, value) in self.skinAttributes:
                # if attrib == "path":
                    # self.path = value
                # if attrib == "language":
                    # self.language = value
                # if attrib == "nexts":
                    # self.nexts = int(value)
                # if attrib == "size":
                    # self.postersize = str(value.split(",")[0])
                    # if int(self.postersize) >= 342:
                        # self.size = "500"
                    # elif int(self.postersize) >= 301:
                        # self.size = "342"
                    # elif int(self.postersize) >= 201:
                        # self.size = "300"
                    # elif int(self.postersize) >= 186:
                        # self.size = "200"
                    # else:
                        # self.size = "185"
            # return Renderer.applySkin(self, desktop, parent)

    def intCheck(self):
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except Exception as e:
            print(e)
            return False

    def changed(self, what):
        if not self.instance:
            return

        if self.instance and not self.suspended:
            if what[0] != self.CHANGED_CLEAR:
                try:
                    self.timer.stop()
                except:
                    pass

                self.timer.start(100, True)
            else:
                self.instance.hide()

    def getEventData(self):
        self.instance.hide()
        serviceRef = None
        eventName = ""

        event = self.source.event

        if event:
            eventName = event.getEventName()
        else:
            return

        service = None

        if isinstance(self.source, ServiceEvent):
            service = self.source.service
            if service:
                serviceRef = str(ServiceReference(service))

        if isinstance(self.source, Event):
            try:
                serviceRef = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
            except Exception as e:
                print(e)

        if isinstance(self.source, EventInfo) and self.source.getEvent():
            try:
                serviceRef = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
            except Exception as e:
                print(e)

        if serviceRef and eventName and "news" not in eventName.lower():
            self.checkExists(eventName, serviceRef)

    def cleantitle(self, title):
        cleanName = re.sub(r"New: ", " ", str(title))
        cleanName = re.sub(r'[\<\>\:\"\/\\\|\?\*\(\)\[\]]', " ", cleanName)
        cleanName = re.sub(r"  ", " ", cleanName)
        cleanName = cleanName.strip()
        return cleanName

    def checkExists(self, eventName, serviceRef):
        eventName = self.cleantitle(str(eventName).replace('\xc2\x86', '').replace('\xc2\x87', ''))
        eventName = eventName.replace('...', '')

        if not os.path.isdir(self.path):
            os.makedirs(self.path)

        posterName = str(self.path) + str(eventName) + ".jpg"
        if os.path.exists(posterName):
            self.showPoster(posterName)

        else:
            start_new_thread(self.downloadPoster, (serviceRef,))

    def showPoster(self, posterName):
        try:
            if self.instance:
                self.instance.setPixmap(loadJPG(posterName))
                self.instance.setScale(1)
                self.instance.show()
        except Exception as e:
            print(e)

    def downloadPoster(self, serviceRef):
        title = ""
        shortDescription = ""
        extendedDescription = ""
        poster = None
        events = None
        eventslist = []
        eventName = ""

        events = ["TES", (serviceRef, 0, -1, -1)]

        eventslist = [] if epgcache is None else epgcache.lookupEvent(events)

        if eventslist:
            if len(eventslist) > 0:
                try:
                    for i in range(self.nexts):
                        srch = "multi"
                        year = None
                        extras = ""

                        if eventslist[i][0]:
                            title = str(eventslist[i][0])

                        eventName = REGEX.sub('', title).strip()
                        eventName = self.cleantitle(title)
                        eventName = eventName.replace('\xc2\x86', '').replace('\xc2\x87', '')
                        eventName = eventName.replace('...', '')

                        if eventslist[i][2]:
                            shortDescription = eventslist[i][2]

                        if eventslist[i][1]:
                            extendedDescription = eventslist[i][1]

                        fullDescription = "%s - %s - %s" % (eventName, shortDescription, extendedDescription)

                        posterName = str(self.path) + str(eventName) + ".jpg"

                        checkTV = [
                            "serial", "series", "serie", "serien", "série", "séries", "serious",
                            "folge", "episodio", "episode", "épisode", "l'épisode", "ep.",
                            "staffel", "soap", "doku", "tv", "talk", "show", "news", "factual", "entertainment", "telenovela",
                            "dokumentation", "dokutainment", "documentary", "informercial", "information", "sitcom", "reality",
                            "program", "magazine", "mittagsmagazin", "т/с", "м/с", "сезон", "с-н", "эпизод", "сериал", "серия"
                        ]

                        checkMovie = [
                            "film", "movie", "фильм", "кино", "ταινία", "película", "cinéma", "cine", "cinema", "filma"
                        ]

                        for i in checkTV:
                            if str(i) in str(fullDescription).lower():
                                srch = "tv"
                                break

                        if srch != "tv":
                            for i in checkMovie:
                                if str(i) in str(fullDescription).lower():

                                    srch = "movie"

                                    match = re.match(r'.*([1-2][0-9]{3})', fullDescription)
                                    if match is not None:
                                        year = match.group(1)

                                    break

                        if not os.path.exists(posterName):

                            if year is not None:
                                extras += "&year=%s" % (year)
                            if self.language is not None:
                                extras += "&language=%s" % (self.language)
                            elif lng is not None:
                                extras += "&language={}".format(lng[:-3])

                            url_tmdb = "http://api.themoviedb.org/3/search/" + str(srch) + "?api_key=" + str(tmdb_api) + "&query=%22" + str(quote(eventName)) + "%22" + extras
                            print("*** url_tmdb ***", url_tmdb)

                            try:
                                temp = json.load(urlopen(url_tmdb))

                                if temp['results']:
                                    poster = temp['results'][0]['poster_path']
                                else:
                                    url_tmdb = "http://api.themoviedb.org/3/search/multi" + "?api_key=" + str(tmdb_api) + "&query=%22" + str(quote(eventName)) + "%22" + extras
                                    temp = json.load(urlopen(url_tmdb))

                                    if temp['results']:
                                        poster = temp['results'][0]['poster_path']
                                    else:
                                        return

                            except Exception as e:
                                print(e)

                            if poster is None:
                                poster = temp['results'][0]['backdrop_path']
                            if poster is not None:
                                url_poster = "https://image.tmdb.org/t/p/w%s%s" % (self.size, poster)

                                download_poster = self.path + str(eventName) + ".jpg"
                                self.savePoster(download_poster, url_poster)

                except Exception as e:
                    print(e)

    def savePoster(self, download_poster, url_poster):
        with open(download_poster, 'wb') as f:
            f.write(urlopen(url_poster).read())

        self.showPoster(download_poster)
