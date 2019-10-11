import time
from .constants import *
from .convert_anilist_to_mal import *
import sys

# returns the file where all id conversions between anilist and mal are kept
def read_convertor_file_as_dict(key='anilist', primary_source='mal'):
	reference = {'key':key}
	key_index = None
	headers = None
	with open(converter_file, 'r') as file:

		for row in file:
			row_col = row.strip().split('\t')

			if row[0] == '#': # log the source of each id column
				row_col[0] = row_col[0].replace('#','') # get rid of header indicator

				for header in row_col: # go through each source
					if key.strip() == header.strip(): # determine the source that will be used as key
						key_index=row_col.index(key)

				if not key_index and not isinstance(key_index, int): # if key index is not set
					if len(row_col) >= 1: # set first column as key index
						key_index = row_col.index(primary_source)
						reference['key'] = primary_source
					else:
						break # if not key index, break (means that the file is empty)

				headers = row_col

			else:
				reference[row_col[key_index]] = {}

				for i in range(0, len(row_col)):
					if i != key_index:
						reference[row_col[key_index]][headers[i]] = row_col[i]

	return reference

# saves data that will be put into file that converts ids
def save_convertor_dict(converter):

	lines=[]
	headers=[converter['key']]
	num_headers = 1

	for key in converter.keys():
		if key == 'key':
			continue

		line = ['']*len(headers)
		line[0] = str(key)

		for source in converter[key]:
			if not source in headers:
				headers.append(source)
				num_headers += 1
				line.extend([''])

			line[headers.index(source)] = str(converter[key][source])

		lines.append(line)

	str_lines = ['\t'.join(headers)]
	for line in lines:
		if len(line) < num_headers:
			line.extend( ['']*(num_headers-len(line)) )

		str_lines.append('\t'.join(line))

	str_lines[0] = '#' + str_lines[0]

	with open(converter_file, 'w+') as file:
		file.write('\n'.join(str_lines))


def update_anime_id_convertor_file(anime_ids, primary_source = 'mal', source = 'anilist', convert_fxn = convert_anilist_to_mal):

	id_converter = read_convertor_file_as_dict(key=source, primary_source=primary_source)

	for anime_id in anime_ids:
		if source == id_converter['key'] and str(anime_id) in id_converter.keys() and \
			 id_converter[str(anime_id)].get(primary_source):

			print('already got it')
			continue

		try:
			primary_id = convert_fxn(anime_id)
		except Exception as e:
			save_convertor_dict(id_converter)
			continue
			# raise e


		anime_id = str(anime_id)
		primary_id = str(primary_id)

		if id_converter['key'] == source:
			if str(anime_id) in id_converter.keys():
				if id_converter[anime_id].get(primary_source):
					continue
			else:
				id_converter[anime_id] = {}

			id_converter[anime_id][primary_source] = primary_id

		else: # if defualt source isnt the key, use primary source
			if str(primary_id) in id_converter.keys():
				if id_converter[primary_id].get(source):
					continue
			else:
				id_converter[primary_id] = {}
			id_converter[primary_id][source] = anime_id


		time.sleep(3)

	save_convertor_dict(id_converter)

	return id_converter