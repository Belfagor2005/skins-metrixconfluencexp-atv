# -*- coding: utf-8 -*-
import os
import sys
import re
import requests
import threading
import glob
import shutil
import json
from Components.config import config
global cur_skin, my_cur_skin, tmdb_api, omdb_api

isz="140,760"

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
    

PY3 = (sys.version_info[0] == 3)
try:
	if PY3:
		from urllib.parse import quote
	else:
		from urllib2 import quote
except:
	pass


try:
	from Components.config import config
	lng = config.osd.language.value
except:
	lng = None
	pass

class bannerXDownloadThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
	def search_tmdb(self,dwn_banner,title,shortdesc,fulldesc,channel=None):
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
			
			
			banner = requests.get(url_tmdb).json()['results'][0]['banner_path'] #banner = json.load(urlopen(url_tmdb))['results'][0]['banner_path']
			if banner:
				url_banner = "https://image.tmdb.org/t/p/w{}{}".format(str(isz.split(",")[0]), banner)
				self.savebanner(dwn_banner, url_banner)
				return True, "[SUCCESS : tmdb] {} => {} => {}".format(title,url_tmdb,url_banner)
			else:
				return False, "[ERROR : tmdb] {} => {} (None)".format(title,url_tmdb)
		except Exception as e:
			if os.path.exists(dwn_banner):
				os.remove(dwn_banner)
			return False, "[ERROR : tmdb] {} => {} ({})".format(title,url_tmdb,str(e))
			
				
	def search_molotov_google(self,dwn_banner,title,shortdesc,fulldesc,channel=None):
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
			banner = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
			if banner.find("molotov"):
				banner = re.sub('\d+x\d+',re.sub(',','x',isz),banner)
				banner = "https://{}".format(banner)
				self.savebanner(dwn_banner, url_banner)
				return True, "[SUCCESS : molotov-google] {} => {} => {}".format(title,url_tmdb,url_banner)
			else:
				return False, "[ERROR : molotov-google] {} => {} (not in molotov site)".format(title,url_tmdb)
		except Exception as e:
			if os.path.exists(dwn_banner):
				os.remove(dwn_banner)
			return False, "[ERROR : molotov-google] {} => {} ({})".format(title,url_tmdb,str(e))

	def search_google(self,dwn_banner,title,shortdesc,fulldesc,channel=None):
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
			banner = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
			url_banner = "https://{}".format(banner)
			self.savebanner(dwn_banner, url_banner)
			return True, "[SUCCESS : google] {} => {} => {}".format(title,url_tmdb,url_banner)
		except Exception as e:
			if os.path.exists(dwn_banner):
				os.remove(dwn_banner)
			return False, "[ERROR : google] {} => {} ({})".format(title,url_tmdb,str(e))

	def savebanner(self, dwn_banner, url_banner):
		with open(dwn_banner,'wb') as f:
			f.write(requests.get(url_banner, stream=True, allow_redirects=True).content) #f.write(urlopen(url_banner).read())
			f.close()


#tpx = bannerXDownloadThread()
#dwn_banner = "test-download-file.jpg"
#print("search_tmdb")	
#val, log = tpx.search_tmdb(dwn_banner,"The Voice is not a MadMax","","")	
#print(log)	
#print("search_molotov_google")	
#val, log = tpx.search_molotov_google(dwn_banner,"The Voice","","")	
#print(log)	
#print("search_google")	
#val, log = tpx.search_google(dwn_banner,"The Voice","","","TF1")	
#print(log)	
