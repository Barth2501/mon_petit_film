from classes.movies_and_series import TVShow

def tvshow():
    # if 'username' not in session or 'id' not in session:
    #     return redirect(url_for('index'))
    tvshow = TVShow.filter_json()
    print(tvshow)
tvshow()
