# -*- coding: utf-8 -*-
# by digiteng...04.2020
# file for skin MetriXconfluencExp by sunriser 07.2021
# <widget render="XParental" source="session.Event_Now" position="315,874" size="50,50" zPosition="3" transparent="1" alphatest="blend"/>
from Components.Renderer.Renderer import Renderer
from Tools.Directories import resolveFilename
from enigma import eLabel, ePixmap, eTimer, loadPNG
import re, os, sys, tempfile
import json
# import config

pratePath = '/usr/share/enigma2/MetriXconfluencExp/logos/parentalrating'
# curskin = config.skin.primary_skin.value.replace('/skin.xml', '')
# pratePath = curskin + '/parental'

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

class XParental(Renderer):

	def __init__(self):
		Renderer.__init__(self)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		try:
			if not self.instance:
				return
			if what[0] == self.CHANGED_CLEAR:
				self.instance.hide()
			if what[0] != self.CHANGED_CLEAR:
				self.delay()
		except:
			pass

	def showParental(self):
		self.event = self.source.event
		if not self.event:
			return
		fd = "{}\n{}\n{}".format(self.event.getEventName(), self.event.getShortDescription(), self.event.getExtendedDescription())
		try:
			pattern = ["\d{1,2}\+"]
			for i in pattern:
				age = re.search(i, fd)
				if age:
					cert = re.sub("\+", "", age.group()).strip()
				else:
					eventNm = REGEX.sub('', self.event.getEventName()).strip().replace('ё','е')
					try:
						infos_file = "{}{}.json".format(pathLoc, eventNm)
						if infos_file:
							with open(infos_file) as f:
								age = json.load(f)['Rated']
							cert = {
									"TV-G": "0",
									"G": "0",
									"TV-Y7": "6",
									"TV-Y": "6",
									"TV-14": "12",
									"TV-PG": "16",
									"PG-13": "16",
									"PG": "16",
									"TV-MA": "18",
									"R": "18",
									"N/A": "UN",
									"Not Rated": "UN",
									"Unrated": "UN",
									"": "UN",
									"Passed": "UN",}.get(age)
					except:
						pass
				if cert:
					self.instance.setPixmap(loadPNG(os.path.join(pratePath, "FSK_{}.png".format(cert))))
					self.instance.show()
				else:
					self.instance.hide()
		except:
			self.instance.hide()

	def delay(self):
		self.timer = eTimer()
		self.timer.callback.append(self.showParental)
		self.timer.start(300, True)

