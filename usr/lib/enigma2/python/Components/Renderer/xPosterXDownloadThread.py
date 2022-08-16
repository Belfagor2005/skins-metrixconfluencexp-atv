# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
import os
import sys
import re
import requests
import threading
import glob
import shutil
import json
from Components.config import config
try:
	lng = config.osd.language.value
except:
	lng = None
	pass

global cur_skin, my_cur_skin, tmdb_api, omdb_api
isz="185,278"
# isz="342,320"
tmdb_api = "9273a48a3cbdcef9484bf45de6f53ff0"
omdb_api = "6a4c9432"

from Components.config import config
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

PY3 = (sys.version_info[0] == 3)
try:
	if PY3:
		from urllib.parse import quote
	else:
		from urllib2 import quote
except:
	pass

class xPosterXDownloadThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.intCheck()

	def intCheck(self):
		import socket
		try:
			socket.setdefaulttimeout(1)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
			return True
		except:
			return False

	def search_tmdb(self,dwn_poster,title,shortdesc,fulldesc,channel=None):
		if self.intCheck():
			try:
				fd = "{}\n{}\n{}".format(title,shortdesc,fulldesc)
				srch = "multi"
				year = None
				url_tmdb = ""

				try:
					pattern = re.findall('[A-Z].+19\d{2}|[A-Z].+20\d{2}', fd)
					pattern = re.findall('\d{4}', pattern[0])
					year = pattern[0]
				except:
					year = None
					pass

				checkMovie = ["film", "movie", "фильм", "кино", "ταινία", "película", "cinéma", "cine", "cinema", "filma"]
				for i in checkMovie:
					if i in fd.lower():
						srch = "movie"
						break

				checkTV = [ "serial", "series", "serie", "serien", "série", "séries", "serious",
							"folge", "episodio", "episode", "épisode", "l'épisode", "ep.",
							"staffel", "soap", "doku", "tv", "talk", "show", "news", "factual", "entertainment", "telenovela",
							"dokumentation", "dokutainment", "documentary", "informercial", "information", "sitcom", "reality",
							"program", "magazine", "mittagsmagazin", "т/с", "м/с", "сезон", "с-н", "эпизод", "сериал", "серия",
							"magazine", "actualité", "discussion", "interview", "débat", "émission", "divertissement", "jeu",
							"information", "météo", "journal", "talk-show", "sport", "culture", "infos", "feuilleton", "téléréalité",
							"société", "clips" ]
				if srch != "movie":
					for i in checkTV:
						if i in fd.lower():
							srch = "tv"
							break

				url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
				if year:
					url_tmdb += "&year={}".format(year)
				if lng:
					url_tmdb += "&language={}".format(lng[:-3])
				poster = requests.get(url_tmdb).json()['results'][0]['poster_path'] #poster = json.load(urlopen(url_tmdb))['results'][0]['poster_path']
				if poster:
					url_poster = "https://image.tmdb.org/t/p/w{}{}".format(str(isz.split(",")[0]), poster)
					self.savePoster(dwn_poster, url_poster)
					return True, "[SUCCESS : tmdb] {} => {} => {}".format(title,url_tmdb,url_poster)
				else:
					return False, "[ERROR : tmdb] {} => {} (None)".format(title,url_tmdb)
			except Exception as e:
				if os.path.exists(dwn_poster):
					os.remove(dwn_poster)
				return False, "[ERROR : tmdb] {} => {} ({})".format(title,url_tmdb,str(e))

	def search_molotov_google(self,dwn_poster,title,shortdesc,fulldesc,channel=None):
		if self.intCheck():
			try:
				headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
				fd = "{}\n{}".format(shortdesc,fulldesc)
				year = None
				try:
					pattern = re.findall('[A-Z].+19\d{2}|[A-Z].+20\d{2}', fd)
					pattern = re.findall('\d{4}', pattern[0])
					year = pattern[0]
				except:
					year = None
					pass
				url_tmdb = "site:molotov.tv+" + quote(title)
				if year:
					url_tmdb += "+{}".format(year)
				url_tmdb = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(url_tmdb)
				ff = requests.get(url_tmdb, stream=True, headers=headers).text
				poster = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
				if poster.find("molotov"):
					poster = re.sub('\d+x\d+',re.sub(',','x',isz),poster)
					url_poster = "https://{}".format(poster)
					self.savePoster(dwn_poster, url_poster)
					return True, "[SUCCESS : molotov-google] {} => {} => {}".format(title,url_tmdb,url_poster)
				else:
					return False, "[ERROR : molotov-google] {} => {} (not in molotov site)".format(title,url_tmdb)
			except Exception as e:
				if os.path.exists(dwn_poster):
					os.remove(dwn_poster)
				return False, "[ERROR : molotov-google] {} => {} ({})".format(title,url_tmdb,str(e))

	def search_google(self,dwn_poster,title,shortdesc,fulldesc,channel=None):
		if self.intCheck():
			try:
				headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
				fd = "{}\n{}".format(shortdesc,fulldesc)
				year = None
				try:
					pattern = re.findall('[A-Z].+19\d{2}|[A-Z].+20\d{2}', fd)
					pattern = re.findall('\d{4}', pattern[0])
					year = pattern[0]
				except:
					year = None
					pass
				#url_tmdb = quote(title) + "%20" + quote(channel)
				url_tmdb = quote(title)
				if year:
					url_tmdb += "+{}".format(year)
				#url_tmdb = url_tmdb + "%20imagesize:" + re.sub(',','x',isz)
				url_tmdb = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(url_tmdb)
				ff = requests.get(url_tmdb, stream=True, headers=headers).text
				poster = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
				url_poster = "https://{}".format(poster)
				self.savePoster(dwn_poster, url_poster)
				return True, "[SUCCESS : google] {} => {} => {}".format(title,url_tmdb,url_poster)
			except Exception as e:
				if os.path.exists(dwn_poster):
					os.remove(dwn_poster)
				return False, "[ERROR : google] {} => {} ({})".format(title,url_tmdb,str(e))

	def savePoster(self, dwn_poster, url_poster):
		with open(dwn_poster,'wb') as f:
			f.write(requests.get(url_poster, stream=True, allow_redirects=True).content) #f.write(urlopen(url_poster).read())
			f.close()


#tpx = xPosterXDownloadThread()
#dwn_poster = "test-download-file.jpg"
#print("search_tmdb")
#val, log = tpx.search_tmdb(dwn_poster,"The Voice is not a MadMax","","")
#print(log)
#print("search_molotov_google")
#val, log = tpx.search_molotov_google(dwn_poster,"The Voice","","")
#print(log)
#print("search_google")
#val, log = tpx.search_google(dwn_poster,"The Voice","","","TF1")
#print(log)