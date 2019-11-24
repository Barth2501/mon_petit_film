import requests
from classes.movies_and_series import *
import time
import json

def add_popular_tvshows():
    res = requests.get(
        'https://api.themoviedb.org/3/tv/popular?api_key=55b1aaf3647ecfaac56c76591cc99a09&language=en-US&page=1')

    res = res.json()

    for k, serie in enumerate(res['results']):
        print()
        print()
        print(serie['name'])
        i = 1
        tvshow = TVShow(name=serie['name'], overview=serie['overview'], genres=serie['genre_ids'],
                   poster_path=serie['poster_path'], vote_average=serie['vote_average'],
                   vote_count=serie['vote_count'], release_date=serie['first_air_date'])
        # Uncomment this line if you want to add tvshows to the mongodb database
        tvshow.save()
        while True:
            address = 'https://api.themoviedb.org/3/tv/' + str(serie['id']) + '/season/' + str(
                i) + '?api_key=' + '55b1aaf3647ecfaac56c76591cc99a09' + '&language=en-US'
            address = requests.get(address)
            if address.status_code == 404:
                break
            else:
                saison = address.json()
                print()
                print('saison', i, saison['name'])
                season = Season(name=saison['name'], number=i, tvShow=tvshow,
                           overview=saison['overview'], poster_path=saison['poster_path'],
                           release_date=saison['air_date'])
                for j, ep in enumerate(saison['episodes']):
                    print('épisode', j+1, ep['name'])
                    episode = Episode(name=ep['name'], number=j+1, season=season,
                                overview=ep['overview'], release_date=ep['air_date'],
                                poster_path=ep['still_path'])
                    season._addEpisode(episode)
                tvshow._addSeasonToDB(season)
                i += 1

def retrieve_genres_list_tvshow():
    res = requests.get('https://api.themoviedb.org/3/genre/tv/list?api_key=55b1aaf3647ecfaac56c76591cc99a09&language=en-US')
    res = res.json()
    with open('genres_list_tvshow.json', 'w') as json_file:
        json.dump(res['genres'], json_file)

def delete_all_tv_shows():
    tvshows = TVShow.filter(id=None)
    for tvshow in tvshows:
        tvshow.delete()
    return True

def test_request():
    serie = requests.get(
        'https://api.themoviedb.org/3/tv/popular?api_key=55b1aaf3647ecfaac56c76591cc99a09&language=en-US&page=1')
    serie = serie.json()
    print(serie['results'][1].keys())
    print()

    saison = 'https://api.themoviedb.org/3/tv/' + str(serie['results'][1]['id']) + '/season/1?api_key=' + '55b1aaf3647ecfaac56c76591cc99a09' + '&language=en-US'
    saison = requests.get(saison)
    saison = saison.json()
    print(saison.keys())
    print()
    
    print(saison['episodes'][0].keys())

delete_all_tv_shows()
add_popular_tvshows()
