import random
import re
import time, sys, copy

from .format_helpers import *

def jikan_anime_format(anime_id, request):
	# print(request)
	#get title elements	


	status = format_string(request.get('status'))
	del request['status']

	title_syn = format_string(request.get('title_synonyms'))
	del request['title_synonyms']

	title_main = format_string(request.get('title'), foreign_chars=True)
	title_eng = format_string(request.get('title_english'), foreign_chars = True)
	title_jpn = format_string(request.get('title_japanese'), foreign_chars=True)

	del request['title']
	del request['title_english']
	del request['title_japanese']


	#get type of anime (TV, OVA, etc.)
	anime_type = format_string(request.get('type'), lower=True)
	del request['type']

	#get synopsis of anime
	synopsis = format_string(request.get('synopsis'))
	if not synopsis or len(synopsis) <= 1:
		synopsis = None
	del request['synopsis']
	
	# get background
	background = format_string(request.get('background'))
	del request['background']

	# get source (ex. original, manga, etc)
	source = format_string(request.get('source'), lower=True)
	del request['source']

	# get air dates
	date_start = format_date(request.get('aired').get('prop').get('from'))
	date_end = format_date(request.get('aired').get('prop').get('to'))
	del request['aired']

	#get genres
	genres = []
	genre_list = request.get('genres')
	if genre_list:
		for genre in genre_list:
			genres.append(format_string(genre.get('name'), lower=True))
	del request['genres']

	#get anime pictures
	pics = get_pics(request)
	del request['image_url']
	del request['pics']


	# get list of related anime. exclude adaptations
	related = {}
	related_list = request.get('related')
	if related_list:
		for item in related_list:
			related[item.lower()] = []
			for show in related_list[item]:
				related[item.lower()].append(int(show.get('mal_id')))
	del request['related']

	#get ops and eds
	anime_ops = format_oped(request.get('opening_themes'))
	anime_eds = format_oped(request.get('ending_themes'))
	
	for op in anime_ops:
		op['type'] = 'op'
	for ed in anime_eds:
		ed['type'] = 'ed'
	anime_ops.extend(anime_eds)
	songs = anime_ops
	del request['opening_themes']
	del request['ending_themes']

	# get premiere season. Ex. spring 2012
	premier_season = request.get('premiered')
	if premier_season:
		premier_season = format_string(premier_season, lower=True)
	del request['premiered']

	# get list of main animating studios
	studios = []
	studio_list = request.get('studios')
	if studio_list:
		for studio in studio_list:
			if studio.get('name'):
				studios.append({
					'studio_id': studio['mal_id'],
					'name':format_string(studio.get('name'), lower = True)
					})
	del request['studios']

	# get episodes
	episodes = request.get('episodes')
	del request['episodes']

	# get list of characters and vas associated with each character
	characters = []
	character_list = request.get('characters')
	if character_list:
		for character in character_list:

			# get voice actors
			voice_actors = []
			if character.get('voice_actors'):
				for va in character.get('voice_actors'):
					voice_actors.append({
							'person_id': va['mal_id'],
							'lang': format_string(va['language'], lower = True)
						})

			characters.append({
					'char_id': character['mal_id'],
					'status': format_string(character['role'], lower=True),
					'persons': voice_actors
				})
	del request['characters']

	# get list of staff
	staff = []
	staff_list = request.get('staff')
	if staff_list:
		for s in staff_list:
			formatted_positions = []
			for position in s['positions']:
				formatted_positions.append(format_string(position, lower=True))
			staff.append({
					'person_id': s['mal_id'],
					'positions': formatted_positions
				})
	del request['staff']

	# get producers
	producers = []
	producer_list = request.get('producers')
	if producer_list:
		for producer in producer_list:
			producers.append({
					'producer_id': producer['mal_id'],
					'name': format_string(producer['name'], lower=True)
				})
	del request['producers']

	# get licensors
	licensors = []
	licensor_list = request.get('licensors')
	if licensor_list:
		for licensor in licensor_list:
			licensors.append({
					'licensor_id': licensor['mal_id'],
					'name': format_string(licensor['name'], lower=True)
				})
	del request['licensors']

	anime_data = {
		'anime_id': anime_id,
		'status': status,
		'title_main': title_main,
		'title_eng': title_eng,
		'title_jpn': title_jpn,
		'title_syn': title_syn,
		'type': anime_type,
		'synopsis': synopsis,
		'background': background,
		'source': source,
		'date_start': date_start,
		'date_end': date_end,
		'genres': genres,
		'pics': pics,
		'related': related,
		'songs': songs,
		'premier_season': premier_season,
		'studios': studios,
		'episodes': episodes,
		'characters': characters,
		'staff': staff,
		'producers': producers,
		'licensors': licensors
	}
	# print('REQUEST')
	# print(request)
	# print('ANIME DATA')
	# for key in anime_data:
	# 	print(key, anime_data[key])
	# print(anime_data)

	#TODO: quality check
	# log any possible errors
	errors = {'anime_id':anime_id}
	for key in anime_data:
		if not key in ['title_syn']:
			if not anime_data[key]:
				errors['content'] = "{} is missing".format(key)

	print('{:7s}: anime data formatted'.format(str(anime_id)))

	return anime_data

def jikan_char_format(char_id, request):

	# get name info
	name_eng = format_name(request.get('name'), foreign_chars = True)
	name_jpn = format_string(request.get('name_kanji'), foreign_chars = True)
	if name_jpn == 'Japanese':
		name_jpn = None
		
	del request['name']
	del request['name_kanji']

	nicknames = format_string_list(request.get('nicknames'))
	del request['nicknames']

	# get description
	description = format_string(request.get('about'))	
	description_null = False
	if description and description.lower() in ['no biography written.']:
		description = None
		description_null = True
	del request['about']

	# get character pics
	pics = get_pics(request)
	del request['image_url']
	del request['pics']

	# try to determine gender of the character. freq of pronouns
	try:
		gender = 2

		if description:
			male = str(description).count(" he ") + str(description).count(" him ") + str(description).count(" his ")
			female = str(description).count(" she ") + str(description).count(" her ") + str(description ).count(" hers ")

			if male > female:
				gender = 1
			elif male < female:
				gender = 0
	except:
		gender = 2

	# get the roles of a character in anime
	animeography = []
	animeography_list = request.get('animeography')
	if animeography_list:
		for anime in animeography_list:

			anime_id = anime.get('mal_id')
			status = format_string(anime.get('role'), lower=True)

			animeography.append({
					'anime_id': int(anime_id),
					'status': status
				})
	del request['animeography']

	# get roles of character in manga
	mangaography = []
	mangaography_list = request.get('mangaography')
	if mangaography_list:
		for manga in mangaography_list:

			manga_id = manga.get('mal_id')
			status = format_string(manga.get('role'), lower=True)

			mangaography.append({
					'manga_id': int(manga_id),
					'status': status
				})
	del request['mangaography'] 

	# del request['voice_actors']

	char_data = {
		'char_id': char_id,
		'name_eng': name_eng,
		'name_jpn': name_jpn,
		'nicknames': nicknames,
		'description': description,
		'pics': pics,
		'gender': gender,
		'animeography': animeography,
		'mangaography': mangaography
		}

	# for key in char_data:
	# 	print(key, char_data[key])

	#TODO: error loggins
	# log any possible errors
	errors = {'char_id':char_id}
	for key in char_data:
		if not key in ['gender', 'nicknames']:
			if key == 'description' and not char_data['description'] and not description_null:
				errors['content'] = "{} is missing".format(key)
			elif not char_data[key]:
				errors['content'] = "{} is missing".format(key)


	print('{:7s}: char data formatted'.format(str(char_id)))
	return char_data

def jikan_person_format(person_id, request):

	# get name
	name_eng = format_name(request.get('name'), foreign_chars = True)
	name_given = format_name(request.get('given_name'), foreign_chars = True)
	name_family = format_name(request.get('family_name'), foreign_chars = True)
	alternate_names = request.get('alternate_names')
	del request['name']
	del request['given_name']
	del request['family_name']
	del request['alternate_names']

	# get description
	description = request.get('about')
	del request['about']

	# get birthday
	birthday = request.get('birthday')
	del request['birthday']

	# get person pics
	pics = get_pics(request)
	del request['image_url']
	del request['pics']

	# get voice acting roles
	va_roles = []
	va_roles_list = request.get('voice_acting_roles')
	if va_roles_list:
		for va_role in va_roles_list:

			anime_id = va_role.get('anime').get('mal_id')
			char_id = va_role.get('character').get('mal_id')

			va_roles.append({
					'anime_id': anime_id,
					'char_id': char_id
				})

	del request['voice_acting_roles']

	# get staff roles
	anime_staff_roles = []
	anime_staff_roles_list = request.get('anime_staff_positions')
	if anime_staff_roles_list:
		for anime_staff_role in anime_staff_roles_list:

			anime_staff_roles.append({
					'anime_id': anime_staff_role.get('anime').get('mal_id'),
					'position': format_string(anime_staff_role['position'], lower=True)
				})

	del request['anime_staff_positions']

	person_data = {
		'person_id': person_id,
		'name_eng': name_eng,
		'name_given': name_given,
		'name_family': name_family,
		'alternate_names': alternate_names,
		'voice_acting_roles': va_roles,
		'anime_staff_roles': anime_staff_roles,
		'birthday': birthday,
		'pics': pics
	}


	# TODO: error logging
	# log any possible errors
	errors = {'person_id':person_id}
	for key in person_data:
		if not person_data[key]:
				errors['content'] = "{} is missing".format(key)

	print('{:7s}: person data formatted'.format(str(person_id)))
	return True, person_data

# returns list of pic urls
def get_pics(request):

	main_img = request.get('image_url')

	if not main_img:
		return []

	pics = [main_img]

	try:
		other_img = request.get('pics')

		if other_img:
			if isinstance(other_img, str):	
				pics.append(other_img)

			elif isinstance(other_img, list):
				if isinstance(other_img[0], dict):
					for img in other_img:
						for key in img:
							pics.append(img[key])
				else:
					pics.extend(other_img)
	except:
		pass

	return pics