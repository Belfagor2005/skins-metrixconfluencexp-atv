from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.Directories import fileExists
from enigma import iServiceInformation
from Components.ConfigList import ConfigListScreen
from Components.Converter.Poll import Poll
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigClock, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.Network import iNetwork

def parse_ipv4(ip):
	ret = ""
	idx = 0
	if ip is not None:
		for x in ip:
			if idx == 0:
				ret += str(x)
			else:
				ret += "." + str(x)
			idx += 1
	return ret

ifaces = iNetwork.getConfiguredAdapters()
ip_list = []
for ip in ifaces:
	ip_list.append((_("IP") + " " + parse_ipv4(iNetwork.getAdapterAttribute(ip, "ip"))))
res = str(ip_list)[2:-2]
open("/tmp/ip.txt", "w").write(str(res))

class ipLoc(Poll, Converter, object):
	IP = 0

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 1000
		self.poll_enabled = True
		self.type = {'ip': self.IP}[type]

	@cached
	def getText(self):
		if self.type == self.IP:
			if fileExists('/tmp/ip.txt'):
				#if fileExists('/etc/network/interfaces'):
				try:
					for line in open('/tmp/ip.txt'):
						if 'IP' in line:
							return line #.split(' ')[1]

				except:
					return
	text = property(getText)
