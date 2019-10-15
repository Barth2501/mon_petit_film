import pandas as pd
import numpy as np
from  matplotlib.pyplot import plot, show
from scipy.sparse.linalg import svds
from app.classes.movies_and_series import Cinema
from app.classes.ratings import Ratings
import numpy as np

movies_df = None
ratings_df = None
Rating = None

def recommend_movies(userID, num_recommendations):

    movies = Cinema.all_values_list(id=1, name=1, _id=0)
    if movies_df is None:
        movies_df = pd.DataFrame(movies)
        movies_df = movies_df.astype({'id':'int32'})
    ratings = Ratings.all_values_list(userId=1, movieId=1, rating=1, _id=0)
    if ratings_df is None:
        ratings_df = pd.DataFrame(ratings)
        ratings_df = ratings_df.astype({'userId':'int32','movieId':'int32','rating':'float32'})

    if Rating is None:
        Rating = ratings_df.pivot(index='userId',columns='movieId',values='rating').fillna(0)

    R = Rating.as_matrix()
    user_ratings_mean = np.mean(R, axis = 1)
    Ratings_demeaned = R - user_ratings_mean.reshape(-1, 1)

    U, sigma, Vt = svds(Ratings_demeaned, k = 50)
    # plot(sigma)
    # show()
    sigma = np.diag(sigma)

    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    preds = pd.DataFrame(all_user_predicted_ratings, columns = Rating.columns)
    
    # Get and sort the user's predictions
    user_row_number = userID - 1 # User ID starts at 1, not 0
    sorted_user_predictions = preds.iloc[user_row_number].sort_values(ascending=False) # User ID starts at 1
    
    # Get the user's data and merge in the movie information.
    user_data = ratings_df[ratings_df.userId == (userID)]
    user_full = (user_data.merge(movies, how = 'left', left_on = 'movieId', right_on = 'movieId').
                     sort_values(['rating'], ascending=False)
                 )

    # print('User {0} has already rated {1} movies.'.format(userID, user_full.shape[0]))
    # print('Recommending highest {0} predicted ratings movies not already rated.'.format(num_recommendations))
    
    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (movies[~movies['movieId'].isin(user_full['movieId'])].
         merge(pd.DataFrame(sorted_user_predictions).reset_index(), how = 'left',
               left_on = 'movieId',
               right_on = 'movieId').
         rename(columns = {user_row_number: 'Predictions'}).
         sort_values('Predictions', ascending = False).
                       iloc[:num_recommendations, :-1]
                      )

    return already_rated, predictions

#already_rated, predictions = recommend_movies(preds, 6850, movies_df, ratings_df, 20)
