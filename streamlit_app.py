import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Tunisian Rami Scorekeeper", page_icon="🃏", layout="wide")

class Player:
    """Represents a player in the Tunisian Rami game."""

    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.round_scores = []

    def update_score(self, score_change: int):
        """Updates the player's score and tracks round history."""
        self.score += score_change
        self.round_scores.append(self.score)
    
    def save_round_scores(self):
        """Saves the round scores in session state."""
        st.session_state.round_scores = self.round_scores

    def load_round_scores(self):   
        """Loads the round scores from session state."""
        self.round_scores = st.session_state.round_scores

    def reset_round_scores(self):
        """Resets the round scores."""
        self.round_scores = []

    def reset_score(self):
        """Resets the player's score."""
        self.score = 0

class TunisianRamiGame:
    """Manages the game logic and state for Tunisian Rami."""

    def __init__(self, player_names: list[str]):
        self.players = {name: Player(name) for name in player_names}
        self.round_history = []  # Correct data structure for round history

    def record_round(self, round_scores: dict[str, int]):  # Corrected type annotation
        """Records the scores for a round and updates player histories."""
        self.round_history.append(round_scores) 
        for name, score_change in round_scores.items():
            self.players[name].update_score(score_change)

    def get_current_scores(self) -> dict[str, int]:
        """Returns a dictionary of current player scores."""
        return {player.name: player.score for player in self.players.values()}

    def get_round_history_dataframe(self) -> pd.DataFrame:
        """Returns a DataFrame showing the score history for each round."""
        df_data = {player.name: player.round_scores 
                   for player in self.players.values()}
        df = pd.DataFrame(df_data)
        df.index.name = "Round"
        df.index += 1
        return df
    def save_game(self, filename="rami_game.json"):
        """Saves the game state to a JSON file."""
        game_data = {
            "players": {name: player.round_scores for name, player in self.players.items()},
            "round_history": self.round_history
        }
        with open(filename, 'w') as f:
            json.dump(game_data, f)

    def load_game(self, filename="rami_game.json"):
        """Loads the game state from a JSON file."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                game_data = json.load(f)

            self.players = {name: Player(name) for name in game_data["players"]}
            for name, round_scores in game_data["players"].items():
                self.players[name].round_scores = round_scores
                self.players[name].score = round_scores[-1] if round_scores else 0

            self.round_history = game_data["round_history"] 
        else:
            st.warning("No saved game found. Starting a new game.")
    def auto_save(self, filename="rami_game.json"):
        """Saves the game state to a JSON file."""
        game_data = {
            "players": {name: player.round_scores for name, player in self.players.items()},
            "round_history": self.round_history
        }
        with open(filename, 'w') as f:
            json.dump(game_data, f)

        st.success("Game saved!")

    def auto_load(self, filename="rami_game.json"):
        """Loads the game state from a JSON file."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                game_data = json.load(f)

            self.players = {name: Player(name) for name in game_data["players"]}
            for name, round_scores in game_data["players"].items():
                self.players[name].round_scores = round_scores
                self.players[name].score = round_scores[-1] if round_scores else 0

            self.round_history = game_data["round_history"]
            st.success("Game Loaded!")
        else:
            st.warning("No saved game found. Starting a new game.")

    def reset_game(self):
        """Resets the game state."""
        self.players = {name: Player(name) for name in self.players}
        self.round_history = []
    



# --- Streamlit App UI ---

st.title("Tunisian Rami Scorekeeper 🃏🇹🇳")

# --- Game Setup (Sidebar) ---
st.sidebar.header("Game Setup")
num_players = st.sidebar.number_input("Number of Players:", min_value=2, max_value=4, value=4)
default_player_names = ["Saleh", "Achref", "Morta", "Khalil"]
player_names = [st.sidebar.text_input(f"Player {i+1} Name:", value=default_player_names[i])
                for i in range(num_players)]
## where to use auto_save and auto_load
## tell
# --- Initialize or Load Game ---
if 'game' not in st.session_state:
    st.session_state.game = TunisianRamiGame(player_names)
game = st.session_state.game

if st.sidebar.button("New Game"):
    game = TunisianRamiGame(player_names)
    st.session_state.game = game
if st.sidebar.button("Save Game"):
    game.save_game()
    st.sidebar.success("Game saved!")
if st.sidebar.button("Load Game"):
    game.load_game()
    st.session_state.game = game
    st.sidebar.success("Game loaded!")


# --- Gameplay Section ---
st.header("Score Adjustments  🎲")
cols = st.columns(len(game.players))
round_scores = {}

for i, (player_name, player) in enumerate(game.players.items()):
    with cols[i]:
        round_scores[player_name] = st.number_input(
            f"Adjust {player_name}'s score:", 
            value=0, 
            key=f"input_{player_name}", # Unique key 
              step=50 
        )

if st.button("Record Round  ➡️"):
    game.record_round(round_scores)
    st.experimental_rerun()  # Refresh the app

# --- Display Scores ---
st.header("Current Scores  🏆")
st.bar_chart(pd.DataFrame([game.get_current_scores()]).transpose())

# --- Round History Table ---
st.header("Round History  📚")
if game.round_history:
    st.table(game.get_round_history_dataframe())
else:
    st.write("No rounds recorded yet.") 

# display round based bars chart each round will display the added scores
st.header("Round Based Scores")
if game.round_history:
    for i, round_scores in enumerate(game.round_history):
        if sum(round_scores.values()) == 0:
            st.subheader(f"Round {i+1} (Frish Round)")

        else:
            st.subheader(f"Round {i+1}")
        st.bar_chart(pd.DataFrame([round_scores]).transpose())
        # if no scores added then its a frish rouncd


        
else:
    st.write("No rounds recorded yet.")

