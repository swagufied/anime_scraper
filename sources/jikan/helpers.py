from utils.request import request_api
from .constants import *
import pickle, os, sys
from utils.file_methods import read_file, save_file
from format.jikan.format_data import jikan_anime_format


def scrape_anime_info(anime_id):

	info_url = "{}/anime/{}".format(api_base_url, anime_id)
	char_url = "{}/anime/{}/characters_staff".format(api_base_url, anime_id)
	pic_url = "{}/anime/{}/pictures".format(api_base_url, anime_id)

	info_request = request_api(info_url)
	char_request = request_api(char_url)
	pic_request = request_api(pic_url)

	char = {'characters': char_request['characters'], 'staff': char_request['staff']}
	pics = {'pics': pic_request['pictures']}
	info_request.update(pics)
	info_request.update(char)


	return info_request


def scrape_character_info(character_id):
 	
	url = "{}/character/{}".format(api_base_url, character_id)
	pic_url = "{}/character/{}/pictures".format(api_base_url, character_id)

	info_request = request_api(url)
	pic_request = request_api(pic_url)

	pics = {'pics': pic_request['pictures']}
	info_request.update(pics)

	return info_request

def scrape_person_info(person_id):
 	
	url = "{}/person/{}".format(api_base_url, person_id)
	pic_url = "{}/person/{}/pictures".format(api_base_url, person_id)

	info_request = request_api(url)
	pic_request = request_api(pic_url)

	pics = {'pics': pic_request['pictures']}
	info_request.update(pics)

	return info_request


def request_and_save(data_id, root_dir, request_fxn, filetype="json", force_refresh=False):
	outdata = None

	filepath = ""
	for root, dirs, files in os.walk(root_dir):
		for file in files:
			file_split = file.split('.')
			if str(file_split[0]) == str(data_id):
				filepath = os.path.join(root, file)

	if not force_refresh and filepath:
		# print('reading file')
		outdata = read_file(filepath)
	else:
		outdata = request_fxn(data_id)
		save_file(outdata, "{}.{}".format(data_id, filetype), root_dir)
	return outdata