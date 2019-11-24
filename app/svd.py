import pandas as pd
import numpy as np
# from  matplotlib.pyplot import plot, show
from scipy.sparse.linalg import svds
from app.classes.movies_and_series import Movie
from app.classes.ratings import Ratings
from app.classes.user import User
import numpy as np
from bson.objectid import ObjectId

import time
movies_df = None

def recommend_movies(userID, num_recommendations):
    start_time3 = time.time()
    
    global movies_df

    movies = Movie.all_values_list(id=1, name=1, genres=1, poster_path=1, _id=0)
    if movies_df is None:
        movies_df = pd.DataFrame(movies)
        movies_df = movies_df.astype({'id':'int32'})
    start_time6 = time.time()
    print("--- load movies df: %s seconds ---" % (start_time6 - start_time3))

    baseRatings = pd.read_csv('./rating_update.csv', header=0)[:100000]
    ratings = User.get(_id=ObjectId(userID)).json['ratings']
    ratings_df = pd.DataFrame(ratings, columns=('cinema','rating'))
    # if ratings_df is None:
    #     ratings_df = pd.DataFrame(ratings, columns=('cinema','rating'))
    ratings_df['userId'] = baseRatings['userId'].max() + 1
    ratings_df = ratings_df.rename(columns = {'cinema':'movieId'})
    ratings_df = ratings_df.astype({'userId':'int32','movieId':'int32','rating':'float32'})

    baseRatings = baseRatings.astype({'userId':'int32','movieId':'int32','rating':'float32'})
    baseRatings = pd.concat([baseRatings,ratings_df], ignore_index=True, sort=False)
    start_time7 = time.time()
    print("--- load rating df: %s seconds ---" % (start_time7 - start_time6))
    Rating = baseRatings.pivot(index='userId',columns='movieId',values='rating').fillna(0)
    R = Rating.to_numpy()
    user_ratings_mean = np.mean(R, axis = 1)
    Ratings_demeaned = R - user_ratings_mean.reshape(-1, 1)
    start_time4 = time.time()
    print("--- construct the pivot %s seconds ---" % (start_time4 - start_time7))

    U, sigma, Vt = svds(Ratings_demeaned, k = 30)
    # plot(sigma)
    # show()
    sigma = np.diag(sigma)

    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    preds = pd.DataFrame(all_user_predicted_ratings, columns = Rating.columns)
    # Get and sort the user's predictions
    user_row_number = (baseRatings['userId'].max()) - 1 # User ID starts at 1, not 0
    sorted_user_predictions = preds.iloc[user_row_number].sort_values(ascending=False) # User ID starts at 1
    # Get the user's data and merge in the movie information.
    user_data = baseRatings[baseRatings.userId == (baseRatings['userId'].max())]

    user_full = (user_data.merge(movies_df, how = 'left', left_on = 'movieId', right_on = 'id').
                     sort_values(['rating'], ascending=False)
                 )

    # print('User {0} has already rated {1} movies.'.format(userID, user_full.shape[0]))
    # print('Recommending highest {0} predicted ratings movies not already rated.'.format(num_recommendations))
    
    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (movies_df[~movies_df['id'].isin(user_full['movieId'])].
         merge(pd.DataFrame(sorted_user_predictions).reset_index(), how = 'left',
               left_on = 'id',
               right_on = 'movieId').
         rename(columns = {user_row_number: 'Predictions'}).
         sort_values('Predictions', ascending = False).
                       iloc[:num_recommendations, :-1]
                      )
    start_time5 = time.time()
    print("--- building the svd %s seconds ---" % (start_time5 - start_time4))
    return user_full, recommendations

#already_rated, predictions = recommend_movies(preds, 6850, movies_df, ratings_df, 20)
