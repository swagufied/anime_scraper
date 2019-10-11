from bs4 import BeautifulSoup
import random
import re
import time
import sys
from bs4 import BeautifulSoup

from server.scrape.utils.file_management import *
from config import USERLIST_STORAGE

#takes username and returns list of series id, title, title synonyms, type, and air dates
#only returns completed animes
def get_animeID(data):

	# soup = request_userlist(username)
	soup = BeautifulSoup(data, 'html.parser')
	if soup == None:
		return None

	animes = soup.find_all('anime')

	anime_list = []
	for b in animes:

		# only get completed animes
		series_status = int(b.series_status.contents[0])
		if series_status != 2:
			continue

		# only get if user has completed them
		user_status = b.my_status.contents[0]
		try:
			if int(user_status) != 2:
				continue
		except:
			if not user_status in ['completed','Completed']:
				continue

		anime_id = b.series_animedb_id.contents[0]
		if not anime_id:
			continue


		synonyms=[]
		if len(b.series_synonyms.contents) > 0:
			synonyms = delim_to_list(b.series_synonyms.contents[0], "; ")


		#TODO: add user watch date
		# anime_list.append({
		# 	'anime_id': str(anime_id),
		# 	'main_title': str(b.series_title.contents[0]),
		# 	'title_synonyms': synonyms
		# 	# start date
		# 	# end date
		# 	})

		anime_list.append(anime_id)

	return anime_list


def save_anime_userlist_file(xml_file):

	address = "{}/{}".format(USERLIST_STORAGE, xml_file.filename)
	if save_file(xml_file, address):
		return address
	else:
		return None


def get_animeID_from_xml(xml_file_address):
	data = get_data(xml_file_address)
	if not data:
		print('xml file not able to be read')
		return None

	return get_animeID(data)