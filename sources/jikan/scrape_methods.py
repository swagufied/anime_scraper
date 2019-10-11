import sys
import pickle
from .constants import *
from .helpers import scrape_anime_info, scrape_character_info, scrape_person_info, request_and_save
from utils.request import request_api

# scrape from top anime (jikan) - all characters and people associated will be scraped as well.
def scrape_top_anime(num, force_refresh=False, check_files=True):
	anime_list = []

	# pull animes until we have enough num anime
	i = 1
	while len(anime_list) < num:

		url = "{}/top/anime/{}".format(api_base_url, i)

		response = request_api(url)

		for anime in response['top']:
			print(anime['mal_id'])
			anime_list.append(anime['mal_id'])

			if len(anime_list) >= num:
				break

		i += 1

	if check_files:

		for anime_id in anime_list:
			print('requesting and saving', anime_id)
			anime = request_and_save(anime_id, anime_dir, scrape_anime_info, force_refresh=force_refresh)
			
			for character in anime['characters']:
				request_and_save(character['mal_id'], character_dir, scrape_character_info, force_refresh=force_refresh)

				for person in character['voice_actors']:
					request_and_save(person['mal_id'], person_dir, scrape_person_info)

	return anime_list

# scrape a single anime
def scrape_anime(anime_id, force_refresh=False, check_files=True):
	anime = request_and_save(anime_id, anime_dir, scrape_anime_info, force_refresh=force_refresh)
	return anime