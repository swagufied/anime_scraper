"""
FORMAT FOR QUESITON TXT FILE
-----------------------------

This script will generate an additional file (in the same directory) for each question txt file that it is run on.
The filename will be <question_file>.processed. Do not delete this file unless the db is reset
That file will keep record of which questions are already in the database

Each question must be formatted as below:

	***	ID||<unique identifier>
	***	question||string
		difficulty||int (1=easy, 2=difficult)
		autocomplete_answer||boolean (True, False)
	***	answers||<answer1.1>::<answer1.2>::<answer1.3>||<answer2.1>::<answer 2.2>||etc.
		category||<category1>||<category2>||etc.
		question_links||<link_type>::<url1>||<link_type>::<url2>||etc. (link_type: 1=picture, 2=video)
		answer_links||<link_type>::<url1>||<link_type>::<url2>||etc. (link_type: 1=picture, 2=video)
		mal_id||<MAL id>||<MAL id>||etc.
		END

Ex.
	question||What is Suzumiya Haruhi?
	difficulty||1
	autocomplete_answer||True
	answers||trash::garbage::laji
	category||what is this
	question_links||1::www.animegirls.com/suzumiya_haruhi
	answer_links||1::www.images.com/garbage
	mal_id||4382
	END

	question||What is Mashiro Shiina?
	difficulty||1
	autocomplete_answer||True
	answers||best girl::waifu||girl::female
	category||what is this
	question_links||1::www.animegirls.com/shiina_mashiiro
	answer_links||1::www.images.com/tenshii
	mal_id||13759
	END


Notes:
- *** indicates mandatory on creation. All other fields can be updated. The script will not run without every field though so just fill them in
- the ID will be autogenerated on the original file. DO NOT TOUCH THIS FIELD the ID will not be used by the database itself. It is merely a tool this script will use to identify new vs. old questions when the txt file is changed and resubmitted to the database.
- similar shows will be grouped under 1 show. However this does mean that if a specific show within the series is searched for, the question will only fall under the mal id specified.
	Ex. 10087 (Fate Zero) and 22297 (Fate UBW) will be placed under the Fate series. If 10087 is set as the mal_id, a search for 22297 questions will not yield the designated question
- input "categories" as all lower case. no punctuation if possible
- answers will be searched in a case insensitive manner. It will be displayed as in the txt file. The first answer following a || will be treated as the main answer and all subsequent answers dileanated by :: will be treated as other acceptable answers
- each complete answer set (main answer and other acceptable synonyms) only needs to be input once. afterwards, only the main answer needs to be filled in for the answer column. If the answer set ever changes, this will result in the first instance of an answer set being used.
Ex. Q1: answer||dog::mammal::warm-blooded
	Q2: answer||dog::mans best friend
	The answer to Q2 will take on the answer set specified in Q1. and the answer set of Q2 will never be processed

	Q1: answer||dog::mammal::warm-blooded
	Q2: answer||dog
	both questions will take on the same answer set

- If you decide to edit questions after logging them into the database, DO NOT CHANGE THE ID. This will result in unwanted outcomes that may not lead to immediately traceable errors. 
- any typos in the tags or  inputs will result in the question being misclassified.
	Ex. questions with inputs "category||<who>" and "category||<whoo>" will be placed in different categories 
- dont add any unnecessary quotation marks. as all inputs will be read as string unless otherwise indicated (ie. int)
-----------------------------------------------------------------------------

USAGE
----------------------------
This script requires Python 3 +

- ensure the constants are properly set then run this file as below:
python upload_questions.py -u <username> -p <password> -f <filepath1>,<filepath2>,etc. (NO SPACES BETWEEN COMMAS AND FILEPATHS)


Notes:
- any errors returned by the server will halt the code. progress up to the point of error will be recorded
- no commas within filepaths
- if there is an error connecting with the server (404 not found error), check the "base_url" in the constants section
"""


 

"""
SCRIPT (dont touch)
"""
import json, sys, os, re
import optparse
import requests
import uuid

#parse filepaths
parser = optparse.OptionParser()
parser.add_option("-u", "--username", action="store",dest="username")
parser.add_option("-p", "--password", action="store",dest="password")
parser.add_option("-f", "--filepaths", action="store",dest="question_files")
options, args = parser.parse_args()

username = options.username
password = options.password
question_files = options.question_files.split(',')

if not username or not password or not question_files:
	raise Exception('username, password, and question_files are required inputs')

# constants
base_url = "http://localhost:5001"


# tracking vars
ids = []

def parse_question(raw_text, update=None):

	return_obj = {
		"ID":None,
		'question': {
			"id":None,
			"text":None,
			"difficulty":None,
			"autocomplete_answer":None,
			"tags":[],
			"answers":[],
			"question_links":[],
			"answer_links":[],
			"shows":[]
		},
		'new': False
	}

	

	columns = raw_text.split("\n")
	for column in columns:
		column = column.split('||')

		if column[0] == "ID":
			if column[1] in ids:
				raise Exception('Duplicate IDs were found in the txt file: {}'.format(column[1]))

			
			return_obj['ID'] = column[1]
			ids.append(column[1])
			if update and column[1] in update:
				return_obj['question']['id'] = update[column[1]]

		elif column[0] == "question":
			if not column[1]:
				raise Exception('question is required field')
			return_obj['question']['text'] = column[1]
		
		elif column[0] == "difficulty":
			if not column[1]:
				continue
			return_obj['question']['difficulty'] = int(column[1])

		elif column[0] == "autocomplete_answer":
			if not column[1]:
				continue
			return_obj['question']['autocomplete_answer'] = bool(column[1])

		elif column[0] == "answers":
			if len(column[1:]) <= 0:
				raise Exception('answers is required field')

			for answer in column[1:]:
				answer = answer.split('::')

				answer_entity = {
					'text': answer[0],
					'children': []
					}

				if len(answer) > 1:
					for child in answer[1:]:
						if not child:
							raise Exception('answer is required field')
						answer_entity["children"].append({
							'text': child
							})
				return_obj['question']['answers'].append(answer_entity)

		elif column[0] == "category":
			for category in column[1:]:
				if not category:
					continue
				return_obj['question']['tags'].append({
					'type': 1,
					'name': category
					})

		elif column[0] == "question_links":
			for raw_link in column[1:]:
				if not raw_link:
					continue
				raw_link = raw_link.split('::')
				return_obj['question']['question_links'].append({
					'type': int(raw_link[0]),
					'url': raw_link[1]
					})

		elif column[0] == "answer_links":
			for raw_link in column[1:]:

				if not raw_link:
					continue
				raw_link = raw_link.split('::')
				return_obj['question']['answer_links'].append({
					'type': int(raw_link[0]),
					'url': raw_link[1]
					})

		elif column[0] == "mal_id":
			for mal_id in column[1:]:
				if not mal_id:
					continue
				return_obj['question']['shows'].append({
					"mal_id": int(mal_id)
					})

	if not return_obj.get('ID'):
		return_obj['ID'] = str(uuid.uuid4())
		return_obj['new'] = True

	return {return_obj['ID']: return_obj['question'], 'new': return_obj['new']}


def read_processed_file(file):
	submitted_questions = {}
	for line in file:
		line_col = line.strip().split('\t')
		submitted_questions[line_col[0]] = line_col[1]
	return submitted_questions

def write_processed_file(processed_file, submitted_questions):

	lines = []
	for id in submitted_questions:
		line = '\t'.join([str(id), str(submitted_questions[id])])
		lines.append(line)

	lines = '\n'.join(lines)

	with open(processed_file, 'w+') as file:
		file.write(lines)


# iterate through provided question files
for question_file in question_files:

	# read submitted questions
	submitted_questions = {}
	if os.path.isfile(question_file + '.processed'):

		submitted_raw_questions = None
		with open(question_file + '.processed', 'r') as file:
			submitted_questions = read_processed_file(file)


	# read new/updated questions
	raw_text = None
	with open(question_file, 'r') as file:
		raw_text = file.read()

	# process questions
	formatted_questions = {}
	raw_questions = raw_text.split('END')

	processed_questions = []

	for raw_question in raw_questions:

		raw_question = raw_question.strip(' \t\n\r')
		if not raw_question:
			continue


		formatted_question = parse_question(raw_question, update=submitted_questions)
		if formatted_question['new']:
			for ID in formatted_question.keys():
				processed_questions.append('ID||{}\n'.format(ID) + raw_question)
				break
		else:
			processed_questions.append(raw_question)

		del formatted_question['new']
		formatted_questions.update(formatted_question)

	# print(processed_questions)

	processed_questions = '\nEND\n\n'.join(processed_questions)
	with open(question_file, 'w+') as file:
		file.write(processed_questions)
	# print(formatted_questions)


	# login
	data = {
		'username': username,
		'password': password
	}
	response = requests.post(base_url + '/api/user/login', json=data)
	tokens = json.loads(response.content)
	if 'errors' in tokens:
		raise Exception('Something went wrong: {}'.format(tokens['errors']))

	# upload questions
	for ID in formatted_questions:

		tags = []
		for tag in formatted_questions[ID]['tags']:
			
			# check if tag already exists
			filter = {
				'and':[]
			}

			for key in tag:
				filter['and'].append({'eq': [key, tag[key]]})

			data = {'filters':filter}

			url = base_url + '/api/question_tag/'
			try:
				response = requests.get(url, json = data)
				response = json.loads(response.content)
			except Exception as e:
				write_processed_file(question_file + '.processed', submitted_questions)
				raise e

			if 'question_tags' in response and len(response['question_tags']) >= 1:
				tag['id'] = response['question_tags'][0]['id']
				tags.append(tag)
			else:

				url = base_url + '/api/question_tag/create'
				try:
					response = requests.post(url, headers = tokens, json = tag)
					response = json.loads(response.content)
				except Exception as e:
					write_processed_file(question_file + '.processed', submitted_questions)
					raise e


				if 'errors' in response:
					write_processed_file(question_file + '.processed', submitted_questions)
					raise Exception('Something went wrong: {}'.format(response['errors']))

				tags.append(response['question_tag'])

			# check if answer set already exists
		answers = []
		for answer in formatted_questions[ID]['answers']:
			url = base_url + '/api/answer/'

			filter = {'eq': ['text', answer['text']]}
			data = {'filters': filter}
			try:
				response = requests.get(url, json = data)
				response = json.loads(response.content)
			except Exception as e:
				write_processed_file(question_file + '.processed', submitted_questions)
				raise e

			if 'answers' in response and len(response['answers']) >= 1:
				answer['id'] = response['answers'][0]['id']
				answers.append(answer)
			else:
				url = base_url + '/api/answer/create'

				try:
					response = requests.post(url, headers = tokens, json = answer)
					response = json.loads(response.content)
				except Exception as e:
					write_processed_file(question_file + '.processed', submitted_questions)
					raise e


				if 'errors' in response:
					write_processed_file(question_file + '.processed', submitted_questions)
					raise Exception('Something went wrong: {}'.format(response['errors']))

				answers.append(response['answer'])

		formatted_questions[ID]['tags'] = tags
		formatted_questions[ID]['answers'] = answers
		# check if question already exists
		if submitted_questions.get(ID):
			url = base_url + '/api/question/{}'.format(submitted_questions[ID])
			# print(formatted_questions[ID])
			try:
				response = requests.put(url, headers = tokens, json = formatted_questions[ID])
				response = json.loads(response.content)
			except Exception as e:
				write_processed_file(question_file + '.processed', submitted_questions)
				raise e
			
			if 'errors' in response:

				if 'missing' in response['errors']:
					pass
				else:
					write_processed_file(question_file + '.processed', submitted_questions)
					raise Exception('Something went wrong: {}'.format(response['errors']))
			else:
				continue


		url = base_url + '/api/question/create'
		# print(formatted_questions[ID])
		try:
			response = requests.post(url, headers = tokens, json = formatted_questions[ID])
			response = json.loads(response.content)
		except Exception as e:
			write_processed_file(question_file + '.processed', submitted_questions)
			raise e
		
		if 'errors' in response:
			write_processed_file(question_file + '.processed', submitted_questions)
			raise Exception('Something went wrong: {}'.format(response['errors']))

		submitted_questions[ID] = response['question']['id']

	write_processed_file(question_file + '.processed', submitted_questions)
	print('File successfully processed: {}'.format(question_file))

print('FINISHED')




