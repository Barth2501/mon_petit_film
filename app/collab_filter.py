from app.views import mongo
import pandas as pd

movies = mongo.db.movies.find({'id': {'$lt':7000} },{'genres':1, 'name':1, 'id':1})
movie_df = pd.DataFrame(movies)
ratings_df = pd.read_csv('./ratings_small.csv')
ratings_df = ratings_df[['userId','movieId','rating']]
ratings_df=ratings_df.dropna()

#ratings = mongo.db.ratings.find({},{'userId':1, 'movieId':1,'rating':1})
#rating_df = pd.DataFrame(ratings)

movie_df = movie_df.dropna()
#L=[]
#for id in movie_df['id']:
#    L.append(int(id))
#movie_df['id']=L
movie_rating_merged_data = movie_df.merge(ratings_df, left_on='id', right_on='movieId', how='inner')