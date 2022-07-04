# -*- coding: utf-8 -*-
#edit lululla to 03.07.2022
#channelselections 
# <widget render="xExtraGenrePic" source="ServiceEvent" position="793,703" size="50,50" zPosition="3" transparent="1" />
#
#infobar
# <widget render="xExtraGenrePic" source="session.Event_Now" position="54,315" size="125,110" zPosition="22" transparent="1" />
# <widget render="xExtraGenrePic" source="session.Event_Next" position="54,429" size="125,110" zPosition="22" transparent="1" />  
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
from Components.config import config
import json
import re
import os
curskin = config.skin.primary_skin.value.replace('/skin.xml', '')
PIC_PATH = '/usr/share/enigma2/%s/genre_pic' %curskin
print('patch pathLoc', PIC_PATH)
if os.path.isdir("/tmp"):
        pathLoc = "/tmp/infos/"
else:
        pathLoc = "/tmp/infos/"

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
                
class xExtraGenrePic(Renderer):

    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = ePixmap

    def postWidgetCreate(self, instance):
        self.changed((self.CHANGED_DEFAULT,))

    def changed(self, what):
        if self.instance:
            if what[0] == self.CHANGED_CLEAR:
                self.instance.setPixmap(None)
            else:
                found = False
                self.event = self.source.event
                if self.event:
                    genreTxt = ""
                    try:
                        # evName = self.event.getEventName()
                        # R = re.compile(r'([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!|/.*|\|\s[0-9]+\+|[0-9]+\+|\s\d{4}\Z|([\(\[\|].*?[\)\]\|])|(\"|\"\.|\"\,|\.)\s.+|\"|:|Премьера\.\s|(х|Х|м|М|т|Т|д|Д)/ф\s|(х|Х|м|М|т|Т|д|Д)/с\s|\s(с|С)(езон|ерия|-н|-я)\s.+|\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|\s(ч|ч\.|с\.|с)\s\d{1,3}.+|\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)
                        # path = "%s%s.json" % (config.plugins.xtraEvent.loc.value + "xtraEvent/infos/", R.sub('', evName).strip())
                        # if os.path.exists(path):
                                # with open(path) as f:
                                        # genreTxt = json.load(f).get("Genre", "").split(",")[0]
                        #lululla edit only with renderer xZZZZZZZZZ
                        eventNm = REGEX.sub("", self.event.getEventName()).strip().replace('ё','е')
                        infos_file = "{}{}.json".format(pathLoc, eventNm)
                        print('Patch name: ', infos_file)
                        if os.path.exists(infos_file):
                            with open(infos_file) as f:
                                genreTxt = json.load(f).get("Genre", "").split(",")[0]  
                                print('genreTxt name: ', genreTxt)
                        #end edit lululla 
                    except Exception as e:
                            print('error get event: ',  str(e))
                            pass
                    if not genreTxt:
                        try:
                            gData = self.event.getGenreData()
                            if gData:
                                genreTxt = {1:('Thriller','Movie','Detective','Adventure','Science','Comedy','Serie','Romance','Serious','Adult'), 2:('News','Weather','Magazine','Docu','Disc'), 3:('Show','Quiz','Variety','Talk'), 4:('Sports','Special','Sports Magazine','Football','Tennis','Team Sports','Athletics','Motor Sport','Water Sport','Winter Sport','Equestrian','Martial Sports'), 5:("Childrens","Children",'entertainment (6-14)','entertainment (10-16)','Information','Cartoon'), 6:('Music','Rock/Pop','Classic Music','Folk','Jazz','Musical/Opera','Ballet'), 7:('Arts','Performing Arts','Fine Arts','Religion','PopCulture','Literature','Cinema','ExpFilm','Press','New Media','Culture','Fashion'), 8:('Social','Magazines','Economics','Remarkable People'), 9:('Education','Nature/Animals/','Technology','Medicine','Expeditions','Social','Further Education','Languages'), 10:('Hobbies','Travel','Handicraft','Motoring','Fitness','Cooking','Shopping','Gardening'), 11:('Original Language','Black & White','Unpublished','Live Broadcast')}.get(gData.getLevel1(),"")[gData.getLevel2()]
                        except:
                            pass
                    # if genreTxt:   #edit lululla 
                    else:
                        png = "%s%s.png" % (PIC_PATH, re.sub("[^0-9a-z]+", "_", genreTxt.lower()).replace("__", "_").strip("_"))
                        if os.path.exists(png):
                            print('png name: ', png)
                            self.instance.setPixmapFromFile(png)
                            self.instance.setScale(1)
                            self.instance.show()
                            found = True
                        print('Found Genre : ', found)
                if not found:
                    self.instance.hide()
