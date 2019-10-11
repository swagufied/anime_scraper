import re
import datetime


"""
CLEAN UP FUNCTIONS
"""
def remove_nonstandard_symbols(string):
	string_final = ''
	for char in string.strip():
		# removes star symbol
		if char == '\u2606':
			string_final += ' '
		string_final += char
	return string_final

def remove_outer_quotation(string):
	string = string.strip()
	if string[0] == '"' and string[-1] == '"':
		return string[1:-2]
	else:
		return string

def remove_outer_parenthesis(string):
	string = string.strip()
	if string[0] == '(' and string[-1] == ')':
		return string[1:-2]
	else:
		return string

def replace_html_num(string):
	string = string.strip()
	string = string.replace('&#044;', ',')
	string = string.replace('&#039;', "'")
	string = string.replace('&#038;', '&')
	string = string.replace('&#034;', '"')
	string = string.replace('&#033;', '!')
	string = string.replace('&#035;', '#')
	stirng = string.replace('&#028;', '(')
	stirng = string.replace('&#029;', ')')

	return string

# removes all multiple whitespaces
def clean_string(string):
	if not string:
		return None
	string = re.sub(' +',' ',string)
	return string

"""
FORMAT FUNCTIONS
"""

def format_string_list(string_list, foreign_chars=False, lower=False):

	if not string_list:
		return []

	final_string_list = []
	for string in string_list:
		final_string_list.append(format_string(string, foreign_chars = foreign_chars, lower=lower))

	return final_string_list

def format_string(string, foreign_chars = False, lower=False):
	if not isinstance(string, str):
		return string
	if not string:
		return None
	string = string.strip()
	if not string:
		return None
	# print(string)
	string = remove_nonstandard_symbols(string)
	# print("symbol remove {}".format(string))
	# if not foreign_chars:
	# 	try:
	# 		string = string.encode(encoding='utf-8').decode('ascii')
	# 	except:
	# 		return None
	if lower:
		string = string.lower()
	string = clean_string(string)
	string = replace_html_num(string)
	# print("html remove {}".format(string))
	string = remove_outer_quotation(string)
	# print("quot remove {}".format(string))
	string = remove_outer_parenthesis(string)
	# print("paren remove {}".format(string))
	return string


# returns datetime obj
def format_date(date_string):

	if not date_string:
		return None
	
	return date_string
	# mdy = date_string.split(delim)

	# try:
	# 	return datetime.datetime(int(mdy[y]), int(mdy[m]), int(mdy[d]))
	# except Exception as e:
	# 	print(e)
	# 	return None


# gets rid of #1: in front of ops and eds
def format_oped(song_list):

	if not song_list:
		return []

	if not isinstance(song_list, list):
		song_list = [song_list]


	oped_info = []

	# search through song list
	for string in song_list:
		#clean up string
		string = format_string(string, foreign_chars = True)

		# remove "#"
		string = re.sub(r'^#.*: *', "", string)
		title = re.findall(r'\"(.*)\"', string)

		#if no title detected, return unparsed song line as title
		if not title:
			return [{
				'title': string,
				'artists': [],
				'episodes': ""
			}]

		# remove title from string since title has been determined
		string = string.replace('"{}"'.format(title[0]), "").strip()

		# find all artists and bands in rest of string
		split_string = re.split(r'(?: *by | ft\. | feat\. | ft | feat |, )(?![^(]*\))', string)

		# print('split stirng: {}'.format(split_string))

		artists = []
		for part in split_string:
			if not part:
				continue

			# parse out episode markings and exclude them from string
			episodes = re.findall(r'(?: |\()(?:ep *|eps *|ep\. *|episodes *|episode *)([0-9\-, ]*)\)', part)
			episodes = ', '.join(episodes)
			episodes_for_exclusion = re.findall(r'((?: |\()(?:ep *|eps *|ep\. *|episodes *|episode *)[0-9\-, ]*\))', part)

			if episodes_for_exclusion:
				for episode in episodes_for_exclusion:
					part = part.replace("{}".format(episode.strip()),"")

			# go through each artist. exclude any artists whose names are only foreign chars (most likely jpn name of english)
			split_part = re.split(r'\(|\)', part)
			for s in split_part:
				# print(s)
				
				if s in [' ','']:
					continue

				if ', ' in s:
					for a in s.split(', '):
						try:
							a.encode(encoding='utf-8').decode('ascii')
							artists.append(a.strip())
						except:
							pass
						
				else:
					try:
						artist = s
						artist.encode(encoding='utf-8').decode('ascii')
						artists.append(artist.strip())
					except:
						pass
		# print(artists)
			
		oped_info.append({
			'title': title[0],
			'artists': artists,
			'episodes': episodes
		})

	return oped_info


def format_name(name_string, foreign_chars = False):
	# print(name_string)
	if not name_string:
		return None

	name_string = format_string(name_string, foreign_chars = foreign_chars)

	split_name = list(reversed(name_string.split(',')))
	split_name = [s.strip() for s in split_name]
	name = ' '.join(split_name)

	return name
	


def format_nicknames(nickname_string):

	if not nickname_string:
		return []

	nickname_string = nickname_string.replace('&quot;', '"')

	indexes = [i for i, char in enumerate(nickname_string) if char == '"']

	# print('nickname: {}'.format(nickname_string))

	if len(indexes) == 2:
		nicknames = nickname_string[indexes[0]+1:indexes[1]]
		nicknames = [n.strip() for n in nicknames.split(', ')]
		# print('split nicknames: {}'.format(nicknames))
		nicknames = [n for n in nicknames if n != ""]
		# print(nicknames)
		return nicknames

	else:
		# print('here')
		return nickname_string

#will take a string and delim by delim provided. returns list with all '' filtered out
def delim_to_list(string, delim):
    delim_list = string.split(delim)
    delim_list = [a for a in delim_list if a != '']
    return delim_list