import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from app.classes.movies_and_series import Movie
from app.classes.ratings import Ratings
from app.classes.user import User
import numpy as np
from bson.objectid import ObjectId
import time


movies_df = None

# Here lies the function which implement the recommended movies prediction,
# It is a very basic recommendation engine as it ony uses singalur value decomposition based
# on a large database of ratings (~1M) on the movies database (~20k)


def recommend_movies(userID, num_recommendations):
    start_time3 = time.time()

    global movies_df
    # We retrieve the movies database from mongodb db if it is not in the cache
    movies = Movie.all_values_list(
        id=1, name=1, genres=1, poster_path=1, _id=0)
    if movies_df is None:
        movies_df = pd.DataFrame(movies)
        movies_df = movies_df.astype({"id": "int32"})
    start_time6 = time.time()
    print("--- load movies df: %s seconds ---" % (start_time6 - start_time3))

    # We retrieve the ratings database from a csv file saved in the folder
    baseRatings = pd.read_csv("./rating_update.csv", header=0)[:300000]

    # We retrieve the user's ratings database and concatenate it to all the ratings we have
    ratings = User.get(_id=ObjectId(userID)).json["ratings"]
    ratings_df = pd.DataFrame(ratings, columns=("cinema", "rating"))
    ratings_df["userId"] = baseRatings["userId"].max() + 1
    ratings_df = ratings_df.rename(columns={"cinema": "movieId"})
    ratings_df = ratings_df.astype(
        {"userId": "int32", "movieId": "int32", "rating": "float32"}
    )
    baseRatings = baseRatings.astype(
        {"userId": "int32", "movieId": "int32", "rating": "float32"}
    )
    baseRatings = pd.concat([baseRatings, ratings_df],
                            ignore_index=True, sort=False)
    start_time7 = time.time()
    print("--- load rating df: %s seconds ---" % (start_time7 - start_time6))

    # We create the pivot database between the movies and the ratings and normalize it
    Rating = baseRatings.pivot(
        index="userId", columns="movieId", values="rating"
    ).fillna(0)
    R = Rating.to_numpy()
    user_ratings_mean = np.mean(R, axis=1)
    Ratings_demeaned = R - user_ratings_mean.reshape(-1, 1)
    start_time4 = time.time()
    print("--- construct the pivot %s seconds ---" %
          (start_time4 - start_time7))

    # We build the singular value decomposition using 30 vectors
    U, sigma, Vt = svds(Ratings_demeaned, k=30)

    # We use this decomposition to estimate ratings of the current user
    sigma = np.diag(sigma)
    all_user_predicted_ratings = np.dot(
        np.dot(U, sigma), Vt
    ) + user_ratings_mean.reshape(-1, 1)
    preds = pd.DataFrame(all_user_predicted_ratings,
                         columns=Rating.columns)

    # We sort the user ratings that we have just estimated
    user_row_number = (baseRatings["userId"].max()) - 1
    sorted_user_predictions = preds.iloc[user_row_number].sort_values(
        ascending=False
    )

    # From the initial movies database, we merge the estimated ratings to
    user_data = baseRatings[baseRatings.userId ==
                            (baseRatings["userId"].max())]
    user_full = user_data.merge(
        movies_df, how="left", left_on="movieId", right_on="id"
    ).sort_values(["rating"], ascending=False)

    # We return the database of the top rated movies for the user according
    # to the number of recommendations we want
    recommendations = (
        movies_df[~movies_df["id"].isin(user_full["movieId"])]
        .merge(
            pd.DataFrame(sorted_user_predictions).reset_index(),
            how="left",
            left_on="id",
            right_on="movieId",
        )
        .rename(columns={user_row_number: "Predictions"})
        .sort_values("Predictions", ascending=False)
        .iloc[:num_recommendations, :-1]
    )
    start_time5 = time.time()
    print("--- building the svd %s seconds ---" % (start_time5 - start_time4))
    return user_full, recommendations
