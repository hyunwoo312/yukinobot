from requests import post
from yukino import manager
from bs4 import BeautifulSoup
class AniList:
    '''
    Anilist object created for the use by yukinobot
    This class contains several functions that allow for querying and mutating
    different AniList animelists
    The functions use 'post' onto 'https://graphql.anilist.co' to
    obtain a json file from the url regarding animes
    '''
    def __init__(self):
        self.url = 'https://graphql.anilist.co'
    
    def __str__(self):
        return 'Anilist object ... for yukinobot'
    
    __repr__=__str__

    def anilist(self):
        with manager.Manager('yukino/data/queries/AL_test.txt') as file:
            query = file.read() 
        variables = {
            'id': 10087#,
        }
        response = post(self.url, json={'query': query, 'variables': variables}).json()
        return response

class MyAnimeList:
    '''
    Myanimelist object created for the sole use by yukinobot
    This class contains several functions that allow for querying
    and also obtaining various data such as staff, artists, production, etc
    from the MAL webpage using webscraping (since MAL api is down as of coding this)
    and returns the data
    This function relies on 'https://myanimelist.net/' for all of its work
    '''
    def __init__(self):
        self.url = 'https://myanimelist.net/'