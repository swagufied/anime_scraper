from sources.jikan.constants import *
from utils.file_methods import *
from .jikan.format_data import jikan_anime_format, jikan_char_format
from sources.anilist.convert_anilist_to_mal import convert_anilist_to_mal

# this function will, given an anime id, continue to scrape all anime related to it until it reaches the parent anime.

def determine_parent(anime_id):

	def get_related(anime, related_ids, earliest):
		if anime.get('related'):
			for relation_type in anime['related']:
				if relation_type != 'adaptation':
					for related_id in anime['related'][relation_type]:
						if related_id not in related_ids:

							#get anime info
							related_anime = scrape_anime(related_id)
							related_anime = jikan_anime_format(related_id, related_anime)
							related_ids.append(related_anime['anime_id'])

							# determine earliest show
							if related['anime_id']

							related_ids.extend(get_related(related_anime))
		
		return related_ids, earliest



	anime = scrape_anime(anime_id)
	anime = jikan_anime_format(anime_id, anime)

	earliest = None
	# determine parent
	
		related_orphans = []
		for related_id in formatted_data['related']:
			result = requests.get('{}/api/show/{}'.format(base_url, related_id), json=data)
			result = json.loads(result.content)

			if 'show' in result:
				# if related show has a parent already
				if result['show'].get('parent_id'):
					formatted_data['parent_id'] = result['show']['parent_id']
				
				# if related show doesnt have parent
				else:
					related_orphans.append(result['show'])
			else:




	anime = scrape_anime(anime_id)
	anime = jikan_anime_format(anime_id, anime)

	# read file
	# format data
	# TODOL go through each related
		# if related file doesnt exist, scrape it
		# get related ids
		# keep going until all related animes have been gatherex
		# store titles, 

	

		# create parent for all orphans


		# scrape for all related anime
	formatted_request = jikan_anime_format(anime_id, info_request)
	for relation_type in formatted_request['related'].keys():
		for related_id in formatted_request['related'][relation_type]:

			# check if anime has already been scraped
			if request_and_save(related_id, ):

			else:
				scrape_anime_info(related_id)



# formats jikan data into one that can be put into the jeopoardy db
def format_jeopardy_table_data(anime_id):

	anime = read_file(anime_dir + '/{}.json'.format(anime_id))
	anime = jikan_anime_format(anime_id, anime)

	mal_id = anime['anime_id']

	# anilist_id = convert_anilist_to_mal(mal_id)
	

	main_title = {
		'title': anime['title_main'],
		'children': []
		}
	# print('main_title', main_title)
	eng = anime['title_eng']
	jpn = anime['title_jpn']
	syn = anime['title_syn']

	raw_titles = []
	if eng:
		if isinstance(eng, list):
			raw_titles.extend(eng)
		else:
			raw_titles.append(eng)

	if jpn:
		if isinstance(jpn, list):
			raw_titles.extend(jpn)
		else:
			raw_titles.append(jpn)

	if syn:
		if isinstance(syn, list):
			raw_titles.extend(syn)
		else:
			raw_titles.append(syn)

	raw_titles = list(set(raw_titles))
	# print('raw_titles', raw_titles)
	
	titles = []
	for title in raw_titles:
		titles.append({'title': title})

	# main_title['children'] = titles


	# print('titles', titles)

	# characters = []
	# for character in anime['characters']:
	# 	char_id = character['char_id']
	# 	character = read_file(character_dir + '/{}.json'.format(char_id))
	# 	character = jikan_char_format(char_id, character)

	# 	main_name = character['name_eng']

	# 	raw_names = [main_name]
	# 	jpn = character['name_jpn']
	# 	nkn = character['nicknames']

	# 	if jpn:
	# 		if isinstance(jpn, list):
	# 			raw_names.extend(jpn)
	# 		else:
	# 			raw_names.append(jpn)

	# 	if nkn:
	# 		if isinstance(nkn, list):
	# 			raw_names.extend(nkn)
	# 		else:
	# 			raw_names.append(nkn)

	# 	names = []
	# 	for name in raw_names:
	# 		names.append({
	# 			'name': name
	# 			})
	# 	characters.append({
	# 		'mal_id': char_id,
	# 		'names': names
	# 	})
	print('main title', main_title)

	return {
		'mal_id': mal_id,
		# 'anilist_id': anilist_id,
		'titles': [main_title]
		# 'characters': characters
	}



