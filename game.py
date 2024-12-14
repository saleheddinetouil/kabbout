import pandas as pd
import os
import json

class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.round_scores = []

    def update_score(self, score_change: int):
        self.score += score_change
        self.round_scores.append(self.score)

    def reset_scores(self):
        self.score = 0
        self.round_scores = []

class TunisianRamiGame:
    def __init__(self, player_names: list[str]):
        self.players = {name: Player(name) for name in player_names}
        self.round_history = []

    def record_round(self, round_scores: dict[str, int]):
        self.round_history.append(round_scores)
        for name, score_change in round_scores.items():
            self.players[name].update_score(score_change)

    def get_current_scores(self) -> dict[str, int]:
        return {player.name: player.score for player in self.players.values()}

    def get_round_history_dataframe(self) -> pd.DataFrame:
        df_data = {player.name: player.round_scores for player in self.players.values()}
        df = pd.DataFrame(df_data)
        df.index.name = "Round"
        df.index += 1
        return df

    def reset_game(self):
        self.players = {name: Player(name) for name in self.players}
        self.round_history = []

    def save_game(self, filename="rami_game.json"):
        game_data = {
            "players": {name: player.round_scores for name, player in self.players.items()},
            "round_history": self.round_history
        }
        with open(filename, 'w') as f:
            json.dump(game_data, f)

    def load_game(self, filename="rami_game.json"):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                game_data = json.load(f)

            self.players = {name: Player(name) for name in game_data["players"]}
            for name, round_scores in game_data["players"].items():
                self.players[name].round_scores = round_scores
                self.players[name].score = round_scores[-1] if round_scores else 0

            self.round_history = game_data["round_history"]
        else:
            raise FileNotFoundError("No saved game found.")
