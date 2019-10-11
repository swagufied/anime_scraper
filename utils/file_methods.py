import os
import json

def save_file(data, filename, root_dir):
	
	if root_dir[-1] != '/':
		root_dir = root_dir + '/'

	filepath = root_dir + filename

	if filename.split('.')[-1] == 'json':
		json_data = json.dumps(data)
		with open(filepath, 'w+') as file:
			file.write(json_data)
	elif filename.split('.')[-1] == 'pkl':
		raise
	else:
		raise Exception('filetype "{}" not supported'.format(filename.split('.')[-1]))

	print('SAVE SUCCESS: {}'.format(filepath))

def read_file(filepath):
	data = None

	if filepath.split('.')[-1] == 'json':
		with open(filepath, 'r') as file:
			data = json.loads(file.read())
	else:
		raise Exception('filetype "{}" not supported'.format(filepath.split('.')[-1]))

	return data


# def determine_filepath(root_dir, filename):

# 	folders = []
# 	for root, dirs, files in os.walk(root_dir):
# 		folders.extend(dirs)

# 	filepath = ""
# 	for folder in folders:
# 		if 

# 	if not filepath:
# 		os.makedirs("{}".format(len(folders)))

# 	return
