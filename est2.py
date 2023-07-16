import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import os
import time
import chess.pgn
from analytics import *
from collections import Counter
from statistics import mean
import re


class ChessAnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("600x400")
        self.title("Chess Pynalytics")
        icon_path = 'icons/pawn.png'
        self.iconphoto(True, tk.PhotoImage(file=icon_path))
        self.app_image = tk.PhotoImage(file=icon_path)

        # Create a menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Create a File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Download Games", command=self.download_games)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Create an Analyze menu
        analyze_menu = tk.Menu(menubar, tearoff=0)
        analyze_menu.add_command(label="Analyze Games", command=self.analyze_games)
        analyze_menu.add_command(label="Rating Distribution", command=self.analyze_rating_distribution)
        analyze_menu.add_command(label="Performance Rating", command=self.analyze_performance_rating)
        analyze_menu.add_command(label="Common Openings", command=self.analyze_common_openings)
        analyze_menu.add_command(label="Average Move Time", command=self.analyze_time_usage)
        analyze_menu.add_command(label="Longest Winning Streak", command=self.analyze_winning_streaks)
        analyze_menu.add_command(label="Longest Losing Streak", command=self.analyze_losing_streaks)
        analyze_menu.add_command(label="Results Timeline", command=self.analyze_results_timeline)
        analyze_menu.add_command(label="Positional Analysis", command=self.analyze_positional_analysis)
        analyze_menu.add_command(label="Game Highlights", command=self.analyze_game_highlighs)
        menubar.add_cascade(label="Analyze", menu=analyze_menu)

        # Create an About menu
        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about_dialog)
        menubar.add_cascade(label="Help", menu=about_menu)

        # Initialize status variable
        self.status_var = tk.StringVar()
        self.status_var.set("Progress: 0.00% (0/0 games)")

        # Create status label
        self.status_label = tk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Create username entry and download button
        self.username_entry = tk.Entry(self, width=20)
        self.username_entry.insert(0, "Enter Username")
        self.username_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.username_entry.bind("<FocusOut>", self.on_entry_focus_out)
        self.username_entry.pack()
        self.download_button = tk.Button(self, text="Download Games", command=self.download_games)
        self.download_button.pack()

        self.username_entry.config(
            fg="gray",
            justify=tk.CENTER,
            relief=tk.SOLID,
            bd=1,
        )

    def show_about_dialog(self):
        about_text = (
            "Version: 1.0\n"
            "Author: konpeki02\n"
            "Copyright (c) 2023\n"
            "MIT License\n\n"
            "Your Working Directory:\n{}\n"
            "\n"
        ).format(os.getcwd())

        about_window = tk.Toplevel(self)
        about_window.title("About")
        about_window.geometry("370x245")
        about_window.iconphoto(True, self.app_image)  # Set the icon image
        about_window.resizable(False, False)  # Disable resizing

        about_frame = tk.Frame(about_window, padx=20, pady=10)
        about_frame.pack(fill=tk.BOTH, expand=True)

        about_label = tk.Label(about_frame, text=about_text, justify=tk.LEFT, anchor="nw", pady=5)
        about_label.pack(side=tk.TOP, anchor=tk.W)

        ok_button = tk.Button(about_window, text="OK", command=about_window.destroy)
        ok_button.pack(side=tk.RIGHT, padx=20, pady=10)

        about_window.transient(self)
        about_window.grab_set()
        about_window.focus_set()
        about_window.wait_window()

    def on_entry_focus_in(self, event):
        if self.username_entry.get() == "chess.com username":
            self.username_entry.delete(0, tk.END)

    def on_entry_focus_out(self, event):
        if not self.username_entry.get():
            self.username_entry.insert(0, "chess.com username")

    def download_games(self):
        username = self.username_entry.get()
        if not username:
            messagebox.showwarning("Warning", "Please enter a username.")
            return

        url = f"https://api.chess.com/pub/player/{username}/games/archives"
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to retrieve archives.")
            return

        archives = response.json().get("archives", [])
        if not archives:
            messagebox.showinfo("Info", "No game archives found.")
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
                            self.update_progress(downloaded_games, total_games)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        messagebox.showinfo("Info", f"All games retrieved and written to: {pgn_filename}")
        messagebox.showinfo("Info", f"Time elapsed: {elapsed_time:.2f} seconds")

    def update_progress(self, downloaded, total):
        progress = downloaded / total * 100
        progress_bar_length = 20
        filled_length = int(progress_bar_length * downloaded / total)
        bar = "█" * filled_length + "-" * (progress_bar_length - filled_length)
        self.status_var.set(f"Progress: [{bar}] {progress:.2f}% ({downloaded}/{total} games)")
        self.update()

    def analyze_games(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        win_count, loss_count, draw_count, total_games = analyze_win_loss(games)
        rating_distribution = analyze_rating_distribution(games)
        performance_rating = analyze_performance_rating(games)
        common_openings = analyze_common_openings(games)
        average_move_time = analyze_time_usage(games)
        longest_winning_streak = analyze_winning_streaks(games)
        longest_losing_streak = analyze_losing_streaks(games)
        results_timeline = analyze_results_timeline(games)
        positional_analysis = analyze_positional_analysis(games)
        game_highlights = analyze_game_highlights(games)

        messagebox.showinfo("Win-Loss Ratio",
                            f"Wins: {win_count}\nLosses: {loss_count}\nDraws: {draw_count}\nTotal Games: {total_games}")
        messagebox.showinfo("Rating Distribution", str(rating_distribution))
        messagebox.showinfo("Performance Rating", f"Performance Rating: {performance_rating}")
        messagebox.showinfo("Most Common Openings", str(common_openings))
        messagebox.showinfo("Average Move Time", f"Average Move Time: {average_move_time}")
        messagebox.showinfo("Winning/Losing Streaks",
                            f"Longest Winning Streak: {longest_winning_streak}\nLongest Losing Streak: {longest_losing_streak}")
        messagebox.showinfo("Game Results Timeline", str(results_timeline))
        messagebox.showinfo("Positional Analysis", str(positional_analysis))
        messagebox.showinfo("Game Highlights", "\n".join(game_highlights))

    def analyze_rating_distribution(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        rating_distribution = analyze_rating_distribution(games)
        messagebox.showinfo("Rating Distribution", str(rating_distribution))

    def analyze_performance_rating(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        performance_rating = analyze_performance_rating(games)
        messagebox.showinfo("Rating Distribution", str(performance_rating))

    def analyze_common_openings(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        common_openings = analyze_common_openings(games)
        messagebox.showinfo("Most Common Openings", str(common_openings))

    def analyze_time_usage(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        average_move_time = analyze_time_usage(games)
        messagebox.showinfo("Average Move Time", f"Average Move Time: {average_move_time}")

    def analyze_winning_streaks(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        longest_winning_streak = analyze_winning_streaks(games)
        messagebox.showinfo("Winning Streaks",
                            f"Longest Winning Streak: {longest_winning_streak}")

    def analyze_losing_streaks(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        longest_losing_streak = analyze_losing_streaks(games)
        messagebox.showinfo("Losing Streaks",
                            f"Longest Losing Streak: {longest_losing_streak}")

    def analyze_results_timeline(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        results_timeline = analyze_results_timeline(games)
        messagebox.showinfo("Game Results Timeline", str(results_timeline))

    def analyze_positional_analysis(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        positional_analysis = analyze_positional_analysis(games)
        messagebox.showinfo("Positional Analysis", str(positional_analysis))

    def analyze_game_highlighs(self):
        pgn_file_path = filedialog.askopenfilename(title="Select PGN File", filetypes=[("PGN Files", "*.pgn")])
        if not pgn_file_path:
            return

        games = []
        with open(pgn_file_path) as file:
            while True:
                game = chess.pgn.read_game(file)
                if game is None:
                    break
                games.append(game)

        game_highlights = analyze_game_highlights(games)
        messagebox.showinfo("Game Highlights", "\n".join(game_highlights))

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = ChessAnalyzerApp()
    app.run()
