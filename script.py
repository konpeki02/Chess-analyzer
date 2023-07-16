import sys

import requests
import os
import time


def download_games(username):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve archives.")
        return

    archives = response.json().get("archives", [])
    if not archives:
        print("No game archives found.")
        return

    pgn_filename = f"{username}_games.pgn"
    total_games = 0
    downloaded_games = 0

    start_time = time.time()

    for archive_url in archives:
        response = requests.get(archive_url)
        if response.status_code == 200:
            games = response.json().get("games", [])
            total_games += len(games)

    with open(pgn_filename, "w") as file:
        for archive_url in archives:
            response = requests.get(archive_url)
            if response.status_code == 200:
                games = response.json().get("games", [])
                for game in games:
                    pgn = game.get("pgn")
                    if pgn is not None:
                        file.write(pgn + "\n\n")
                        downloaded_games += 1
                        print_progress(downloaded_games, total_games)

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    print(f"\nAll games retrieved and written to: {pgn_filename}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")


def print_progress(downloaded, total):
    progress = downloaded / total * 100
    progress_bar_length = 20
    filled_length = int(progress_bar_length * downloaded / total)
    bar = "█" * filled_length + "-" * (progress_bar_length - filled_length)
    print(f"Progress: [{bar}] {progress:.2f}% ({downloaded}/{total} games)", end="\r", flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter the username: ")
    download_games(username)
