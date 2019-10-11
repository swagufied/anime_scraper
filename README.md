**Anime Scraper**

This tool is meant to be used in conjunction with the question server found [here](https://github.com/swagufied/anime-trivia). Scripts are provided to automate interactions with the database with minimal work on the user end. Of course one can also interact directly with its API as well.

**Script Provided**

The specific instructions for running each script and the arguments are provided at the top of each script file.

- upload_answers.py - this script will upload/update answer sets 

- upload_questions.py - this script will upload/update questions

- add_anime_to_db.py - this script will scrape anime either by pulling the top N number of anime as ranked on MAL or by using a MAL userlist.

**Requirements**
The only requirements are Python 3+ and [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).