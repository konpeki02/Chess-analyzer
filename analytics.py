import chess.pgn
from collections import Counter
from statistics import mean
import re


def analyze_win_loss(games):
    total_games = len(games)
    results = [game.headers.get("Result") for game in games]
    win_count = results.count("1-0")
    loss_count = results.count("0-1")
    draw_count = results.count("1/2-1/2")
    return win_count, loss_count, draw_count, total_games


def analyze_rating_distribution(games):
    ratings = [int(game.headers.get("WhiteElo", 0)) for game in games]
    ratings.extend([int(game.headers.get("BlackElo", 0)) for game in games])
    rating_counts = Counter(ratings)
    return rating_counts


def analyze_performance_rating(games):
    performance_ratings = []
    for game in games:
        white_rating = int(game.headers.get("WhiteElo", 0))
        black_rating = int(game.headers.get("BlackElo", 0))
        if "Result" in game.headers:
            result = game.headers["Result"]
            if result == "1-0":
                performance_ratings.append(white_rating)
            elif result == "0-1":
                performance_ratings.append(black_rating)
            elif result == "1/2-1/2":
                performance_ratings.append((white_rating + black_rating) // 2)
    return mean(performance_ratings) if performance_ratings else 0


def analyze_common_openings(games, top_n=25):
    openings = Counter(game.headers.get("ECO", "") for game in games if game.headers.get("ECO"))
    return openings.most_common(top_n)


def analyze_time_usage(games):
    move_times = []
    time_pattern = re.compile(r"(\d+):(\d+):([\d.]+)")
    for game in games:
        for node in game.mainline():
            comment = node.comment
            if comment and "[%clk" in comment:
                match = time_pattern.search(comment)
                if match:
                    hours, minutes, seconds = match.groups()
                    total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    move_times.append(total_seconds)
    average_move_time = mean(move_times) if move_times else 0
    return average_move_time


def analyze_winning_streaks(games):
    streaks = []
    current_streak = 0
    for game in games:
        if game.headers["Result"] == "1-0":
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
                current_streak = 0
    longest_streak = max(streaks) if streaks else 0
    return longest_streak


def analyze_losing_streaks(games):
    streaks = []
    current_streak = 0
    for game in games:
        if game.headers["Result"] == "0-1":
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
                current_streak = 0
    longest_streak = max(streaks) if streaks else 0
    return longest_streak


def analyze_results_timeline(games):
    result_timeline = [(game.headers["Result"], game.headers["Date"]) for game in games]
    return result_timeline


def analyze_positional_analysis(games):
    positions = Counter(game.headers.get("Opening", "") for game in games)
    return positions


def analyze_game_highlights(games, num_moves=5):
    highlights = []
    for game in games:
        moves = []
        node = game
        for _ in range(num_moves):
            node = node.variations[0] if node.variations else None
            if node is None:
                break
            moves.append(node.move)
        highlights.append(" ".join(str(move) for move in moves))
    return highlights


def analyze_games(pgn_file):
    games = []
    with open(pgn_file) as file:
        while True:
            game = chess.pgn.read_game(file)
            if game is None:
                break
            games.append(game)

    win_count, loss_count, draw_count, total_games = analyze_win_loss(games)
    rating_distribution = analyze_rating_distribution(games)
    performance_rating = analyze_performance_rating(games)
    common_openings = analyze_common_openings(games)
    # average_move_time = analyze_time_usage(games)
    longest_winning_streak = analyze_winning_streaks(games)
    longest_losing_streak = analyze_losing_streaks(games)
    # results_timeline = analyze_results_timeline(games)
    # positional_analysis = analyze_positional_analysis(games)
    # game_highlights = analyze_game_highlights(games)

    print("Win-Loss Ratio:")
    print(f"Wins: {win_count}")
    print(f"Losses: {loss_count}")
    print(f"Draws: {draw_count}")
    print(f"Total Games: {total_games}")
    print()

    print("Rating Distribution:")
    for rating, count in rating_distribution.items():
        print(f"Rating: {rating} - Count: {count}")
    print()

    print("Performance Rating:")
    print(f"Performance Rating: {performance_rating}")
    print()

    print("Most Common Openings:")
    for opening, count in common_openings:
        print(f"Opening: {opening} - Count: {count}")

    # print("Time Usage:")
    # print(f"Average Move Time: {average_move_time}")
    # print()

    print("Winning/Losing Streaks:")
    print(f"Longest Winning Streak: {longest_winning_streak}")
    print(f"Longest Losing Streak: {longest_losing_streak}")
    print()

    # create a calendar that lights up if more or less losses or maybe by elo loss?
    # print("Game Results Timeline:")
    # for result, date in results_timeline:
    #     print(f"Result: {result} - Date: {date}")
    # print()

    # print("Positional Analysis:")
    # for position, count in positional_analysis.items():
    #     print(f"Position: {position} - Count: {count}")
    # print()

    # print("Game Highlights:")
    # for highlight in game_highlights:
    #     print(f"Moves: {highlight}")
    # print()


if __name__ == '__main__':
    pgn_file = "png_files/lichess_AlbertaOil_2023-01-31.pgn"  # Replace with the actual path to your PGN file

    analyze_games(pgn_file)
