"""
ABOUT
---------------------------------------------------------------
This script will a list of anime based on the following options:
	- top - given an integer N, N top most popular anime as ranked on mal will be added to the database
	- mal_user - given a mal username, the list of anime that are marked as completed will be added to the database

USAGE
---------------------------------------------------------------
This script requires Python 3 +

- ensure the constants are properly set then run this file as below:
python add_anime_to_db.py -u <username> -p <password> -m <method> -i <method input>. (NO SPACES BETWEEN COMMAS AND FILEPATHS)

"""

"""
SCRIPT - dont touch
"""
import os
import requests
import json
from sources.jikan.scrape_methods import scrape_top_anime
from format.jeopardy_input import format_jeopardy_table_data
from sources.anilist.id_convert import read_convertor_file_as_dict
from constants import base_url



import json, sys, os, re
import optparse
import requests
import uuid

#parse filepaths
parser = optparse.OptionParser()
parser.add_option("-u", "--username", action="store",dest="username")
parser.add_option("-p", "--password", action="store",dest="password")
parser.add_option("-m", "--method", action="store",dest="method")
parser.add_option("-i", "--method-input", action="store",dest="method_input")
options, args = parser.parse_args()

username = options.username
password = options.password
method = options.method
method_input = options.method_input




base_url = "https://anime-trivia-api.herokuapp.com"

anime_ids = None
if method == "top":
	anime_ids = scrape_top_anime(100)
elif method == "userlist"
	anime_ids = 

login_data = {
	'username': username,
	'password': password
}

id_converter = read_convertor_file_as_dict(key='mal', primary_source='anilist')

for anime_id in anime_ids:
	formatted_data = format_jeopardy_table_data(anime_id)

	if id_converter.get(str(anime_id)):
		formatted_data['anilist_id'] = id_converter[str(anime_id)].get('anilist')


	print('logging in')

	tokens = requests.post('{}/api/user/login'.format(base_url), json=login_data)
	tokens = json.loads(tokens.content)

	print('creating characters')
	characters = []
	for character in formatted_data['characters']:

		# check if char is already in db
		data = {
			'filters': {'eq': ['mal_id', character['mal_id']]}
		}
		result = requests.get('{}/api/character/'.format(base_url), json=data)
		search_result = json.loads(result.content)

		if len(search_result['characters']) > 1:
			print('more than 1 char have the same mal id')
			raise

		elif len(search_result['characters']) == 1:
			result = requests.put('{}/api/character/{}'.format(base_url, search_result['characters'][0]['id']), headers=tokens, json=character)
			result = json.loads(result.content)

			if 'character' in result:
				characters.append(result['character'])
			print('UPDATED', result)

		# if no such character exists
		else:
			result = requests.post('{}/api/character/create'.format(base_url), headers=tokens, json=character)
			result = json.loads(result.content)

			if 'character' in result:
				characters.append(result['character'])
			print('CREATED', result)

	print('creating show')
	formatted_data['characters'] = characters

	data = {
		'filters': {'eq': ['mal_id', formatted_data['mal_id']]}
	}

	result = requests.get('{}/api/show/'.format(base_url), json=data)
	search_result = json.loads(result.content)

	if len(search_result) > 1:
		print('more than 1 show have the same mal id')
		raise

	elif len(search_result) == 1:
		result = requests.put('{}/api/show/{}'.format(base_url, search_result[0]['id']), headers=tokens, json=formatted_data)
		result = json.loads(result.content)

		if 'character' in result:
			characters.append(result['character'])
		print('UPDATED', result)

	# if no such show exists
	else:
		result = requests.post('{}/api/show/'.format(base_url), headers=tokens, json=formatted_data)
		result = json.loads(result.content)
		print('CREATED', result)
