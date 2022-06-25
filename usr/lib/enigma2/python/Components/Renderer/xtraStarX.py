# -*- coding: utf-8 -*-
# by digiteng
# v1 07.2020, 11.2021
# for channellist
# <widget source="ServiceEvent" render="xtraStarX" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# or
# <widget source="ServiceEvent" render="xtraStarX" pixmap="xtra/star.png" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
#edit lululla 05-2022
# <ePixmap pixmap="MetriXconfluencExp/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Now" render="xtraStarX" pixmap="MetriXconfluencExp/star.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# <ePixmap pixmap="MetriXconfluencExp/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Next" render="xtraStarX" pixmap="MetriXconfluencExp/star.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider
from Components.config import config
import os
import re
import json


if os.path.isdir("/tmp"):
	pathLoc = "/tmp/infos/"
else:
	pathLoc = "/tmp/infos/"
if not os.path.exists(pathLoc):
	os.mkdir(pathLoc)
    
REGEX = re.compile(
		r'([\(\[]).*?([\)\]])|'
		r'(: odc.\d+)|'
		r'(\d+: odc.\d+)|'
		r'(\d+ odc.\d+)|(:)|'
		
		r'!|'
		r'/.*|'
		r'\|\s[0-9]+\+|'
		r'[0-9]+\+|'
		r'\s\d{4}\Z|'
		r'([\(\[\|].*?[\)\]\|])|'
		r'(\"|\"\.|\"\,|\.)\s.+|'
		r'\"|:|'
		r'\*|'
		r'Премьера\.\s|'
		r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
		r'(х|Х|м|М|т|Т|д|Д)/с\s|'
		r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
		r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
		r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
		r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
		r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)

class xtraStarX(VariableValue, Renderer):
	def __init__(self):
		Renderer.__init__(self)
		VariableValue.__init__(self)
		self.__start = 0
		self.__end = 100

	GUI_WIDGET = eSlider
	def changed(self, what):
		rtng = 0
		if what[0] == self.CHANGED_CLEAR:
			(self.range, self.value) = ((0, 1), 0)
			return
		try:
			event = ""
			evntNm = ""
			evnt = ""
			event = self.source.event
			if event:
				evnt = event.getEventName()
				evntNm = REGEX.sub('', evnt).strip()
				rating_json = "{}{}.json".format(pathLoc, evntNm)
				if os.path.exists(rating_json):
					with open(rating_json) as f:
						rating = json.load(f)['imdbRating']
					if rating:
						rtng = int(10*(float(rating)))
					else:
						rtng = 0
				else:
					rtng = 0
			else:
				rtng = 0
		except:
			pass
		range = 100
		value = rtng

		(self.range, self.value) = ((0, range), value)

	def postWidgetCreate(self, instance):
		instance.setRange(self.__start, self.__end)

	def setRange(self, range):
		(self.__start, self.__end) = range
		if self.instance is not None:
			self.instance.setRange(self.__start, self.__end)

	def getRange(self):
		return self.__start, self.__end

	range = property(getRange, setRange)
