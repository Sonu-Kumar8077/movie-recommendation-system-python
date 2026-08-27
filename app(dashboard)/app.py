import os
import pickle
import requests
import pandas as pd
import streamlit as st


# -----------------------------
# Load data and similarity model
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "movies_dict.pkl"), "rb") as file:
    movies_dict = pickle.load(file)

with open(os.path.join(BASE_DIR, "similarity.pkl"), "rb") as file:
    similarity = pickle.load(file)

# Convert dictionary into DataFrame
movies = pd.DataFrame(movies_dict)


# -----------------------------
# Fetch movie poster
# -----------------------------

def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        return None

    url = (
        f"https://api.themoviedb.org/3/movie/"
        f"{movie_id}?api_key={api_key}&language=en-US"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path

    except requests.RequestException:
        return None

    return None


# -----------------------------
# Recommendation function
# -----------------------------

def recommend(movie):

    movie_index = movies[movies["title"] == movie].index[0]

    # Similarity scores for selected movie
    distances = similarity[movie_index]

    # Sort movies according to similarity
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i, score in movies_list:

        movie_id = movies.iloc[i]["movie_id"]

        recommended_movies.append(
            movies.iloc[i]["title"]
        )

        recommended_movies_posters.append(
            fetch_poster(movie_id)
        )

    return recommended_movies, recommended_movies_posters


# -----------------------------
# Streamlit UI
# -----------------------------

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie",
    movies["title"].values
)


# -----------------------------
# Show recommendations
# -----------------------------

if st.button("Show Recommendation"):

    recommended_movie_names, recommended_movie_posters = recommend(
        selected_movie_name
    )

    cols = st.columns(5)

    for col, name, poster in zip(
        cols,
        recommended_movie_names,
        recommended_movie_posters
    ):

        with col:

            st.subheader(name)

            if poster:
                st.image(
                    poster,
                    use_container_width=True
                )
            else:
                st.warning("Poster unavailable")