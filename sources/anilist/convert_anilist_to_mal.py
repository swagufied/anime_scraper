import requests
import json

from .constants import *

# converts anilist id to mal id
def convert_anilist_to_mal(anilist_id):

	query = """
	 query ($userId: Int = %s) { # Define which variables will be used in the query (id)
      Media (id: $userId){
      idMal
    	}
  	}
	""" % (str(anilist_id))
	request = requests.post(base_url, json={'query': query})
	request = json.loads(request.content)

	if request.get('errors'):
		msg = request['errors']
		raise Exception(msg)

	print('anilist_id', anilist_id)
	print('mal id', request['data']['Media']['idMal'])

	return int(request['data']['Media']['idMal'])

