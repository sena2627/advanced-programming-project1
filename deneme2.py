import streamlit as st
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


spotify_client_id = '6ca7fbbd2e80456fa8e46225699bbbdc'
spotify_client_secret = '22e45d9962894bde9d1807de5fd3a9d2'

class User:
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f"Welcome, {self.username}!"

def get_spotify_song(query):
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret))
    results = sp.search(q=query, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'id': track['id']
        }
    return None

def get_song_genres(song_id):
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret))
    track = sp.track(song_id)
    artist_id = track['artists'][0]['id']
    artist_info = sp.artist(artist_id)
    return artist_info.get('genres', [])

def get_song_details_by_name(song_name):
    song = get_spotify_song(song_name)
    if not song:
        return f"'{song_name}', no results found."

    genres = get_song_genres(song['id'])

    file_path = "songs.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            songs_data = json.load(file)
            lyrics = None
            for category in songs_data:
                for song_entry in category['songs']:
                    if song_entry['title'].lower() == song_name.lower():
                        lyrics = song_entry['lyrics']
                        break
                if lyrics:
                    break
    except FileNotFoundError:
        lyrics = None

    return {
        'name': song['name'],
        'artist': song['artist'],
        'genres': genres,
        'lyrics': lyrics if lyrics else "No results found."
    }

def count_word_occurrences(lyrics, word):
    import re
    return len(re.findall(rf"\b{re.escape(word)}\b", lyrics, re.IGNORECASE))

def get_best_recommendation(word, songs):
    recommendations = []

    for category in songs:
        for song in category['songs']:
            count = count_word_occurrences(song['lyrics'], word)
            if count > 0:
                spotify_data = get_spotify_song(song['title'])
                genres = get_song_genres(spotify_data['id']) if spotify_data else []
                recommendations.append({
                    'title': song['title'],
                    'artist': song['artist'],
                    'lyrics': song['lyrics'],
                    'count': count,
                    'genres': genres,
                    'spotify_id': spotify_data['id'] if spotify_data else None
                })

    recommendations.sort(key=lambda x: x['count'], reverse=True)
    return recommendations

def display_recommendations(recommendations):
    if not recommendations:
        st.write("No Results Found.")
        return

    st.subheader("The Song That Contains Your Word The Most:")
    best = recommendations[0]
    st.write(f"- **Song:** {best['title']}")
    st.write(f"- **Artist:** {best['artist']}")
    st.write(f"- **Genres:** {', '.join(best['genres']) if best['genres'] else 'Unknown Genre'}")
    st.write(f"- **Lyrics:** {best['lyrics'][:100]}...")

    st.subheader("Other Songs:")
    for i, song in enumerate(recommendations[1:], start=1):
        st.write(f"{i}. **Song:** {song['title']}")
        st.write(f"   **Artist:** {song['artist']}")
        st.write(f"   **Genres:** {', '.join(song['genres']) if song['genres'] else 'Unknown Genre'}")

def get_genre_suggestions(genre):
    genre_suggestions = {
        'pop': ['Blinding Lights', 'Shape of You', 'Levitating', 'Dance Monkey', 'Watermelon Sugar', 'Don\'t Start Now'],
        'rock': ['Bohemian Rhapsody', 'Stairway to Heaven', 'Hotel California', 'Sweet Child O\' Mine', 'Smells Like Teen Spirit', 'Imagine'],
        'jazz': ['So What', 'Take Five', 'Feeling Good', 'My Favorite Things', 'Autumn Leaves', 'All Blues', 'Blue Monk'],
        'hip-hop': ['Sicko Mode', 'HUMBLE.', 'God\'s Plan', 'Rockstar', 'Old Town Road', 'Savage', 'WAP', 'Highest in the Room'],
        'classical': ['Fur Elise', 'Canon in D', 'The Four Seasons', 'Symphony No. 9', 'Ride of the Valkyries', 'Moonlight Sonata'],
     }
    suggestions = genre_suggestions.get(genre, [])
    return suggestions

def display_genre_suggestions(genre):
    suggestions = get_genre_suggestions(genre)
    if not suggestions:
        st.write(f"'{genre}', no results found from this genre.")
        return

    st.subheader(f"{genre.capitalize()}, Suggested Songs for This Genre:")
    for i, song in enumerate(suggestions, start=1):
        st.write(f"{i}. **Song:** {song}")

def main():
    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.title("Music Search")
        st.subheader("Please enter a username to proceed.")
        username = st.text_input("Username:")
        if st.button("Proceed") and username:
            st.session_state.user = User(username)
            st.success(f"Welcome, {username}!")
    else:
        user = st.session_state.user
        st.sidebar.title("Choose your need")
        st.sidebar.write(str(user))
        choices = st.sidebar.radio("Choose your need",
                                   ["Home", "1-Search with a Song's Name", "2-Search with a Song's Lyric", "3-Get Suggestions for a Song Genre"])

        if choices == "Home":
            st.title("Welcome to Multifunctional Music Search App")
            st.subheader("Discover your favorite songs with ease.")
            st.markdown("*Whether you're trying to find the lyric to your favorite song, find a song from a piece of lyric, or explore music based on your favorite genres, we've got you covered.*")
            st.subheader("Features")
            st.markdown("1. Search with a Song's Name")
            st.markdown("2. Search with a Song's Lyric")
            st.markdown("3. Get Song Suggestions by the Choice of a Genre")

        elif choices == "1-Search with a Song's Name":
            st.subheader("Welcome to Search with a Song's Name Section")
            st.markdown("*Can't remember the lyrics to that catchy tune stuck in your head? Just enter the song name and we'll fetch the lyrics for you instantly.*")
            st.markdown("--------------------------------------------------------")
            st.subheader("How It Works")
            st.markdown("**Simple Search: Type the song name in our search bar and get instant access to lyrics and more...**")

            song_name = st.text_input("Enter the song name:")
            if st.button("Search"):
                details = get_song_details_by_name(song_name)
                st.write(details)

        elif choices == "2-Search with a Song's Lyric":
            st.subheader("Welcome! Here, you can search with lyrics to find song's name.")
            st.markdown("*Have a few lines of a song but can't recall its name? No problem! Enter the lyrics you remember, and we'll identify the song for you.*")
            st.markdown("-----------------------------------------------------------")
            st.subheader("How It Works")
            st.markdown("*After entering your lyric, the results given to you are songs that contains the words you searched for the most.*")
            st.markdown("*It will only display a few of the songs that contains your search.*")
            st.markdown("*It might not give you the song you searched for.*")
            search_word = st.text_input("Enter a word to search in lyrics:")
            file_path = "songs.json"
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    songs_data = json.load(file)

                if st.button("Search"):
                    recommendations = get_best_recommendation(search_word, songs_data)
                    display_recommendations(recommendations)
            except FileNotFoundError:
                st.write("Songs data file not found. Please upload songs.json.")

        elif choices == "3-Get Suggestions for a Song Genre":
            st.subheader("We can even make suggestions for you by the choice of a genre.")
            st.markdown("*Looking to explore new music? **Choose your favorite genres**, and we'll recommend songs you'll love.*")

            genre = st.radio("Select a genre", ('pop', 'rock', 'jazz', 'hip-hop', 'classical'))
            if st.button("Search"):
                display_genre_suggestions(genre)

if __name__ == "__main__":
    main()
