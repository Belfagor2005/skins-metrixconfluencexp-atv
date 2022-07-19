# -*- coding: utf-8 -*-
# by lululla 07.2021
# <ePixmap blend="blend" pixmap="ZSkin-FHD/icons/ip.png" position="1207,925" size="30,35" zPosition="2" />
# <widget render="ZIp" source="session.Event_Now" position="1242,925" size="250,37" font="Regular; 24" halign="left" zPosition="4" foregroundColor="blue" backgroundColor="#202020" transparent="0" />
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText
from enigma import eLabel, eTimer
import json
import re
import os

        
class ZIp(Renderer, VariableText):
    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.intCheck()

    def intCheck(self):
        import socket
        try:
            socket.setdefaulttimeout(0.5)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except:
            return False

    GUI_WIDGET = eLabel
    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            self.text = ''
        else:
            self.delay()

    def infoip(self):
        if self.downloading:
            return
        self.downloading = True
        try:
            if self.intCheck():
                if not os.path.exists('/tmp/currentip'):
                    os.system('wget -qO- http://ipecho.net/plain > /tmp/currentip')
                currentip1 = open('/tmp/currentip', 'r')
                currentip = currentip1.read()
                self.text = "WAN %s" %(str(currentip))
                print('text= ', self.text)
        except:
            if os.path.exists("/tmp/currentip"):
                os.remove("/tmp/currentip")
            return ""

    def delay(self):
        self.downloading = False
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.infoip)
        except:
            self.timer_conn = self.timer.timeout.connect(self.infoip)
        self.timer.start(250, False)
