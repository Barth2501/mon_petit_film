import requests
from classes.movies_and_series import *
import time
import json

def add_popular_tvshows():
    res = requests.get(
        'https://api.themoviedb.org/3/tv/popular?api_key=55b1aaf3647ecfaac56c76591cc99a09&language=en-US&page=1')

    res = res.json()

    b = TVShow.get(name='The Mandalorian')

    for k, serie in enumerate(res['results']):
        i = 1
        a = TVShow(serie['name'], overview=serie['overview'],
                   poster_path=serie['poster_path'], vote_average=serie['vote_average'])
        # Uncomment this line if you want to add tvshows to the mongodb database
        a.save()
        while True:
            address = 'https://api.themoviedb.org/3/tv/' + str(serie['id']) + '/season/' + str(
                i) + '?api_key=' + '55b1aaf3647ecfaac56c76591cc99a09' + '&language=en-US'
            saison = requests.get(address)
            if saison.status_code == 404:
                break
            else:
                saison = saison.json()
                s = Season(name=saison['name'], number=i, tvShow=a,
                           overview=saison['overview'], poster_path=saison['poster_path'])
                for j, ep in enumerate(saison['episodes']):
                    e = Episode(name=ep['name'], number=j+1, season=s,
                                overview=ep['overview'], globalRating=ep['vote_average'])
                i += 1
        print(a.json)

add_popular_tvshows()

def add_genre_to_popular_tvshows():
    res = requests.get(
        'https://api.themoviedb.org/3/tv/popular?api_key=55b1aaf3647ecfaac56c76591cc99a09&language=en-US&page=1')

    res = res.json()
    for k, serie in enumerate(res['results']):
        print(k,serie['name'])
        TVShow.update_one({'name': serie['name']}, {'$set': {'genres': serie['genre_ids']}})

def retrieve_genres_list_tvshow():
    res = requests.get('https://api.themoviedb.org/3/genre/tv/list?api_key=55b1aaf3647ecfaac56c76591cc99a09&language=en-US')
    res = res.json()
    with open('genres_list_tvshow.json', 'w') as json_file:
        json.dump(res['genres'], json_file)
