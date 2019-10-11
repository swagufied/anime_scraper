
import requests, json
from .constants import *

# converts anilist ids of a userlist to mal ids

def get_anilist_anime_ids(username):

	query = """
	query ($name: String = "%s") { # Define which variables will be used in the query (id)
	  User (name: $name) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
		id
	  }
	}
	""" % (username)

	request = requests.post(base_url, json={'query': query})
	# print(request)
	request = json.loads(request.content)
	query = """
	query ($userId: Int = %s) { # Define which variables will be used in the query (id)
	  MediaListCollection (userId: $userId,  type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
		lists {
		  name
		  isCustomList
		  isSplitCompletedList
		  status
		  entries {
			mediaId
			}
		}
	  }
	}
	""" % request['data']['User']['id']
	request = requests.post(base_url, json={'query': query})
	request = json.loads(request.content)
	# print(request)
	watched_anime_ids = []
	for anime_list in request['data']['MediaListCollection']['lists']:
		if anime_list['name'].lower() == 'completed':
			for entry in anime_list['entries']:

				watched_anime_ids.append(entry['mediaId'])
	
	return watched_anime_ids