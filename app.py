import streamlit as st
import pickle
import pandas as pd
import requests
import base64
import gdown  # For downloading from Google Drive
import os  # Missing import added

# Function to download large files from Google Drive
def download_file_from_google_drive(file_id, output_path):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)

# Google Drive file IDs
MOVIE_DICT_FILE_ID = "1Ate4IZw4m4LdsxB7d_rPKbgGIho39ZVm"
SIMILARITY_FILE_ID = "1MR77X4pML-XqWf80v3qzCiHQXh9LiQOs"

# Download files if they don't exist locally
if not os.path.exists("movie_dict.pkl"):
    download_file_from_google_drive(MOVIE_DICT_FILE_ID, "movie_dict.pkl")

if not os.path.exists("similarity.pkl"):
    download_file_from_google_drive(SIMILARITY_FILE_ID, "similarity.pkl")

# Load movie dictionary and convert to DataFrame
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Fetch movie poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=63ecda3b80f9c3f7819723dd06be9108&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', None)
    
    # Handle missing poster case
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "https://via.placeholder.com/500"  # Placeholder if no poster is available

# Recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# Function to encode image as Base64
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None  # Handle missing image case

# Set background image
bg_image = get_base64("assets/b3.jpg")
if bg_image:
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{bg_image}");
                background-size: cover;
                background-position: center;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Streamlit UI
st.title('Movie Recommender System')

# Dropdown for selecting a movie
selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

# Button for recommendation
if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)
    if len(names) >= 5:
        with col1:
            st.text(names[0])
            st.image(posters[0])
        with col2:
            st.text(names[1])
            st.image(posters[1])
        with col3:
            st.text(names[2])
            st.image(posters[2])
        with col4:
            st.text(names[3])
            st.image(posters[3])
        with col5:
            st.text(names[4])
            st.image(posters[4])
    else:
        st.warning("Not enough recommendations available.")
