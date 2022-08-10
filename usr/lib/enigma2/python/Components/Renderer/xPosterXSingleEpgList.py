# -*- coding: utf-8 -*-
# by beber...03.2022,
# 03.2022 several enhancements : several renders
# for channel,
# <widget source="session.CurrentService" render="xPosterXSingleEpgList" position="800,540" size="900,150" noWrap="1" font="Regular;32" foregroundColor="grey" />
# for epg, event
# <widget source="session.Event_Now" render="xPosterXSingleEpgList" position="800,540" size="900,150" noWrap="1" font="Regular;32" foregroundColor="grey" />
# <widget source="Event" render="xPosterXSingleEpgList" position="800,540" size="900,150" noWrap="1" font="Regular;32" foregroundColor="grey" />
from Components.VariableText import VariableText
from Components.Renderer.Renderer import Renderer
from enigma import eLabel, eEPGCache
from time import localtime
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.CurrentService import CurrentService
from Components.Sources.EventInfo import EventInfo
from Components.Sources.Event import Event
import NavigationInstance

class xPosterXSingleEpgList(Renderer, VariableText):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.epgcache = eEPGCache.getInstance()

	GUI_WIDGET = eLabel

	def changed(self, what):
		evt = None
		text = ""
		try:
			if isinstance(self.source, ServiceEvent):
				service = self.source.getCurrentService()
			elif isinstance(self.source, CurrentService):
				service = self.source.getCurrentServiceRef()
			elif isinstance(self.source, EventInfo):
				service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()	
			elif isinstance(self.source, Event):
				service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()	
			evt = self.epgcache.lookupEvent(['IBDCT', (service.toString(), 0, -1, -1)])
		except:
			self.text = "xx:xx No data\nxx:xx No data\nxx:xx No data\nxx:xx No data\n"
			return

		if evt:
			maxx = 0
			for x in evt:
				if maxx > 0:
					if x[4]:
						t = localtime(x[1])
						text = text + "%02d:%02d %s\n" % (t[3], t[4], x[4])
					else:
						text = text + "n/a\n"

				maxx += 1
				if maxx > 5:
					break

		self.text = text
