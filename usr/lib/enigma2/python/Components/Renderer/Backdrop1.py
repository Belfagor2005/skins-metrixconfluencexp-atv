# -*- coding: utf-8 -*-
# by digiteng...04.2020
# file for skin slyk-q-1080 by sunriser 07.2021
#
# for infobar,
# <widget source="session.Event_Now" render="BackdropX" position="100,100" size="680,1000" />
# <widget source="session.Event_Next" render="BackdropX" position="100,100" size="680,1000" />
# <widget source="session.Event_Now" render="BackdropX" position="100,100" size="680,1000" nexts="2" />
# <widget source="session.CurrentService" render="BackdropX" position="100,100" size="680,1000" nexts="3" />
# for ch,
# <widget source="ServiceEvent" render="BackdropX" position="100,100" size="680,1000" />
# <widget source="ServiceEvent" render="BackdropX" position="100,100" size="680,1000" nexts="2" />
# for epg, event
# <widget source="Event" render="BackdropX" position="100,100" size="680,1000" />
# <widget source="Event" render="BackdropX" position="100,100" size="680,1000" nexts="2" />

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG, eEPGCache, getBestPlayableServiceReference
from Components.Pixmap import Pixmap
from time import gmtime
import sys
import os
import re
import socket
import json
from Components.config import config
global cur_skin, my_cur_skin, tmdb_api, omdb_api
tmdb_api = "9273a48a3cbdcef9484bf45de6f53ff0"
omdb_api = "6a4c9432"
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

path_folder = "/tmp/backdrop/"
if os.path.isdir("/media/hdd"):
    path_folder = "/media/hdd/backdrop/"
elif not os.path.isdir("/media/usb"):
    path_folder = "/media/usb/backdrop/"
else:
    path_folder = "/tmp/backdrop/"
if not os.path.isdir(path_folder):
    os.makedirs(path_folder)             
try:
    from Components.config import config
    lng = config.osd.language.value
except:
    lng = None
    pass
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

class Backdrop1(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.intCheck()

    def intCheck(self):
        try:
            socket.setdefaulttimeout(1)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except:
            return False

    GUI_WIDGET = ePixmap
    def changed(self, what):
        try:
            if not self.instance:
                return
            if what[0] == self.CHANGED_CLEAR:
                self.instance.hide()
            if what[0] != self.CHANGED_CLEAR:
                self.showPoster()
        except:
            pass

                
                
    def showPoster(self):
        self.instance.hide()
        self.event = self.source.event
        if self.event is None:
            self.instance.hide()
            return
        if self.event:
            self.delay2()
            eventNm = REGEX.sub('', self.event.getEventName()).strip().replace('ё','е')
            pstrNm = "{}{}.jpg".format(path_folder, eventNm)
            if not os.path.exists(pstrNm):
                self.downloadPoster(eventNm)
            if os.path.exists(pstrNm):
                self.instance.setPixmap(loadJPG(pstrNm))
                self.instance.show()
        else:
            self.instance.hide()
            return

    def downloadPoster(self, eventNm):
        if self.intCheck():
        
            self.year = self.filterSearch()
            try:
                    url_tmdb = "http://api.tmdb.org/3/search/{}?api_key={}&query={}".format(self.srch, tmdb_api, quote(eventNm))
                    if self.year != None:
                            url_tmdb += "&year={}".format(self.year)
                    if lng:
                            url_tmdb += "&language={}".format(lng[:-3])
            
                    poster = json.load(urlopen(url_tmdb))["results"][0]["backdrop_path"]
                    if poster:
                            url_poster = "http://image.tmdb.org/t/p/w500{}".format(poster)
                            dwn_poster = "{}{}.jpg".format(path_folder, eventNm)
                            with open(dwn_poster, "wb") as f:
                                f.write(urlopen(url_poster).read())
            except:
                    pass

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
            pstrNm = "{}{}.jpg".format(path_folder, eventNm)
            if not os.path.exists(pstrNm):
                self.downloadPoster(eventNm)
        return

    def delay2(self):
        self.timer = eTimer()
        self.timer.callback.append(self.dwn)
        self.timer.start(2000, True)

    def dwn(self):
        start_new_thread(self.epgs, ())
