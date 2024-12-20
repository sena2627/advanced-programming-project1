import json
from collections import Counter


def load_songs(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def get_best_recommendation(input_word, songs_data):
    best_song = None
    max_count = 0

    for entry in songs_data:
        if entry['input'] == input_word:
            for song in entry['songs']:
                word_count = Counter(song['lyrics'].lower().split())[input_word.lower()]
                if word_count > max_count:
                    max_count = word_count
                    best_song = {
                        'title': song['title'],
                        'artist': song['artist'],
                        'word_count': max_count,
                        'lyrics': song['lyrics']
                    }

    return best_song


def list_all_songs(songs_data):
    for entry in songs_data:
        print(f"Input: {entry['input']}")
        for song in entry['songs']:
            print(f"  - {song['title']} by {song['artist']}")

if __name__ == "__main__":
   
    songs_json_path = "songs.json"  
    songs_data = load_songs(songs_json_path)

    user_input = input("Enter a word: ").strip()

    recommendation = get_best_recommendation(user_input, songs_data)

    if recommendation:
        print(f"\nRecommended Song:\n- Title: {recommendation['title']}\n- Artist: {recommendation['artist']}\n- Word Count: {recommendation['word_count']}\n")
    else:
        print("\nSorry, no song was found for this word.")