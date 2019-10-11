from config import DATA_STORAGE
from bs4 import BeautifulSoup
from server.scrape.utils.request import *
from server.scrape.utils.file_management import *
from server.scrape.utils.scrape_utils import *
import os, re

mal_urlbase = 'https://myanimelist.net'
char_list_filepath = "{}/mal/html_charlist".format(DATA_STORAGE)
char_data_filepath = "{}/mal/character".format(DATA_STORAGE)
anime_data_filepath = "{}/mal/anime".format(DATA_STORAGE)

def scrape_char_info(char_id):
	
	search_path = char_data_filepath
	filename = "{}.html".format(char_id)
	url = '{}/character/{}/'.format(mal_urlbase, char_id)
	
	data = scrape_data(search_path, filename, url)	

	bs = BeautifulSoup(data, 'html.parser')
	if not bs:
		return None

	nicknames = None
	name = bs.find_all('h1', class_=re.compile('h1'))
	if name and len(name) == 1:
		name = name[0].contents
		nicknames = re.findall(r"\"(.+)\"", str(name))
		if len(nicknames) == 1:
			nicknames = nicknames[0]
			# name_eng =  re.sub(r'^#.*: *', "", string)

		else:
			nicknames = None
	
	char_data = {
		'nicknames': nicknames
	}

	return char_data

def scrape_anime_info(anime_id):

	search_path = anime_data_filepath
	filename = "{}.html".format(anime_id)
	url = '{}/anime/{}/'.format(mal_urlbase, anime_id)
	
	data = scrape_data(search_path, filename, url)

	bs = BeautifulSoup(data, 'html.parser')
	if not bs:
		return None

	main_title = re.findall(r"<div><h1 class *= *\"h1\"><span itemprop *= *\"name\">(.*)</span></h1>", str(bs))
	if main_title:
		main_title = main_title[0]

	anime_data = {
		'main_title': main_title
	}	

	return anime_data


def scrape_char_list(anime_id):

	search_path = char_list_filepath
	filename = "{}.html".format(anime_id)
	url = '{}/anime/{}/anime_chars/characters'.format(mal_urlbase, anime_id)
	
	data = scrape_data(search_path, filename, url)	


	bs = BeautifulSoup(data, 'html.parser')

	if not bs:
		return None

	final_charlist = []
	temp_list = []
	chars = bs.find_all('a', href=re.compile('https://myanimelist\.net/character/'))
	for char in chars[:-5]:
		char_id = re.findall(r"href *= *\"https://myanimelist\.net/character/([0-9]*)/", str(char))
		role = re.findall(r"<small>(.*)</small>", str(char.find_next_sibling()))


		# get list of voice actors for each character
		va_list = char.find_parent("td").find_next("td").find_all('a', href = re.compile("https://myanimelist\.net/people/"))
		persons = []
		temp_person_list = []
		for person in va_list:
			person_id = re.findall(r"href *= *\"https://myanimelist\.net/people/([0-9]*)/", str(person))
			language = re.findall(r"<small>(.*)</small>", str(person.find_next_sibling("small")))

			if (not person_id or len(person_id) > 1 or not language or len(language) > 1) and not person_id in temp_person_list:
				continue

			try:
				person_id = int(person_id[0])
				language = language[0].lower()
			except Exception as e:
				print(e)
				continue

			persons.append({
				'person_id': person_id,
				'language': language
				})

		if (not role or len(role) > 1 or not char_id or len(char_id) > 1) and not char_id in temp_list:
			continue


		try:
			char_id = int(char_id[0])
			role = role[0].lower()
		except Exception as e:
			print(e)
			continue

		char_info = {
			'role': role,
			'char_id': char_id,
			'persons': persons
			}

		final_charlist.append(char_info)
		temp_list.append(char_id)
	# print(final_charlist)
	print('"{}" character list formatted.'.format(anime_id))
	return final_charlist