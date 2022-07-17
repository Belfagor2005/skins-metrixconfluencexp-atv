# -*- coding: utf-8 -*-
# by digiteng...07.2021,
# 08.2021(stb lang support),
# 09.2021 mini fixes
# © Provided that digiteng rights are protected, all or part of the code can be used, modified...
# russian and py3 support by sunriser...
# downloading in the background while zaping...
# by beber...03.2022,
# 03.2022 specific for EMC plugin ...
# for emc plugin,
# <widget source="Service" render="PosterXEMC" position="100,100" size="185,278" />
from __future__ import absolute_import
from __future__ import print_function
from Components.Renderer.PosterXDownloadThread import PosterXDownloadThread
from Components.Renderer.Renderer import Renderer
from Components.Sources.CurrentService import CurrentService
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.ServiceEvent import ServiceEvent
from ServiceReference import ServiceReference
from enigma import ePixmap, loadJPG, eEPGCache
from enigma import eTimer
import NavigationInstance
import os
import sys
import re
import time
import socket
PY3 = (sys.version_info[0] == 3)
try:
    if PY3:
        import queue
        from _thread import start_new_thread
    else:
        import Queue
        from thread import start_new_thread
except:
    pass

epgcache = eEPGCache.getInstance()
try:
    from Components.config import config
    lng = config.osd.language.value
except:
    lng = None
    pass

path_folder = "/tmp/xemc/"
if os.path.isdir("/media/hdd"):
    path_folder = "/media/hdd/xemc/"
elif not os.path.isdir("/media/usb"):
    path_folder = "/media/usb/xemc/"
else:
    path_folder = "/tmp/xemc/"
if not os.path.isdir(path_folder):
    os.makedirs(path_folder)

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


if PY3:
    pdb = queue.LifoQueue()
else:
    pdb = Queue.LifoQueue()

class PosterDBEMC(PosterXDownloadThread):
    def __init__(self):
        PosterXDownloadThread.__init__(self)
        self.logdbg = None

    def run(self):
        self.logDB("[QUEUE] : Initialized")
        while True:
            canal = pdb.get()
            self.logDB("[QUEUE] : {} : {}-{} ({})".format(canal[0],canal[1],canal[2],canal[5]))
            dwn_xemc = path_folder + canal[5] + ".jpg"
            if os.path.exists(dwn_xemc):
                os.utime(dwn_xemc, (time.time(), time.time()))
            if not os.path.exists(dwn_xemc):
                val, log = self.search_tmdb(dwn_xemc,canal[2],canal[4],canal[3])
                self.logDB(log)
            if not os.path.exists(dwn_xemc) and lng == "fr_FR":
                val, log = self.search_molotov_google(dwn_xemc,canal[2],canal[4],canal[3],canal[0])
                self.logDB(log)
            if not os.path.exists(dwn_xemc):
                val, log = self.search_google(dwn_xemc,canal[2],canal[4],canal[3],canal[0])
                self.logDB(log)
            pdb.task_done()

    def logDB(self, logmsg):
        if self.logdbg:
            w = open(path_folder + "PosterDBEMC.log", "a+")
            w.write("%s\n"%logmsg)
            w.close()

threadDB = PosterDBEMC()
threadDB.start()

class PosterXEMC(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.canal = [None,None,None,None,None,None]
        self.intCheck()
        self.timer = eTimer()
        self.timer.callback.append(self.showPoster)
        self.logdbg = None

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value,) in self.skinAttributes:
            attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    def intCheck(self):
        import socket
        try:
            socket.setdefaulttimeout(1)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except:
            return

    GUI_WIDGET = ePixmap
    def changed(self, what):
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
        if what[0] != self.CHANGED_CLEAR:
            try:
                if isinstance(self.source, ServiceEvent): # source="Service"
                    self.canal[0] = None
                    self.canal[1] = self.source.event.getBeginTime()
                    self.canal[2] = self.source.event.getEventName()
                    self.canal[3] = self.source.event.getExtendedDescription()
                    self.canal[4] = self.source.event.getShortDescription()
                    self.canal[5] = self.source.service.getPath().split(".ts")[0]+".jpg"
                elif isinstance(self.source, CurrentService): # source="session.CurrentService"
                    self.canal[0] = None
                    self.canal[1] = None
                    self.canal[2] = None
                    self.canal[3] = None
                    self.canal[4] = None
                    self.canal[5] = self.source.getCurrentServiceReference().getPath().split(".ts")[0]+".jpg"
                else:
                    self.logPoster("Service : Others")
                    self.canal = [None,None,None,None,None,None]
                    self.instance.hide()
                    return
            except Exception as e:
                self.logPoster("Error (service) : "+str(e))
                self.instance.hide()
                return
            try:
                self.logPoster("Service : {} - {}".format(self.canal[1],self.canal[5]))
                if os.path.exists(self.canal[5]):
                    self.timer.start(100, True)
                elif self.canal[1]:
                    self.logPoster("Downloading poster...")
                    canal = self.canal[:]
                    pdb.put(canal)
                    start_new_thread(self.waitPoster, ())
                else:
                    self.logPoster("No canal detected...")
                    self.instance.hide()
                    return
            except Exception as e:
                self.logPoster("Error (reading file) : "+str(e))
                self.instance.hide()
                return


    def showPoster(self):
        if self.intCheck():
            self.instance.hide()
            if self.canal[5]:
                pstrNm = path_folder + self.canal[5] + ".jpg"
                if os.path.exists(pstrNm):
                    self.logPoster("[LOAD : showPoster] {}".format(spstrNm))
                    self.instance.setPixmap(loadJPG(spstrNm))
                    self.instance.setScale(2)
                    self.instance.show()

    def waitPoster(self):
        if self.intCheck():
            self.instance.hide()
            if self.canal[5]:
                pstrNm = path_folder + self.canal[5] + ".jpg"
                loop = 180
                found = None
                self.logPoster("[LOOP : waitPoster] {}".format(pstrNm))
                while loop>=0:
                    if os.path.exists(pstrNm):
                        if os.path.getsize(pstrNm) > 0:
                            loop = 0
                            found = True
                    time.sleep(0.8)
                    loop = loop - 1
                if found:
                    self.timer.start(10, True)

    def logPoster(self, logmsg):
        if self.logdbg:
            w = open(path_folder + "PosterXEMC.log", "a+")
            w.write("%s\n"%logmsg)
            w.close()

